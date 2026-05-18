import mariadb
from datetime import datetime, timedelta
import pytz, json
from flask import current_app, g, session
from dateutil.relativedelta import relativedelta
from . import version, credentials

class Javascript:
    def __init__(self, prefix:str, app:str, user:str):
        if user is None: user = "--"
        self.__js = {'PREFIX':prefix, 'APP':app, 'USER':user, 'form_submit':'no'}
        self.__outline = "const SERVER_OPTIONS = "
    def add(self, attr:dict):
        self.__js.update(attr)
    def getOut(self) -> str:
        for key, value in self.__js.items():
            if isinstance(value, list):
                self.__js[key] = str(value).replace("'", '"')
            elif not isinstance(value, str):
                self.__js[key] = str(value)
        return self.__outline + str(self.__js)

    @staticmethod
    def toOptions(rows:list[dict]) -> str:
        opts = ""
        for elem in rows:
            opts += "<option value=\"" + str(elem["id"]) + "\">" + elem["bezeichnung"] + "</option>"
        return opts
    

class Configure:
    def __init__(self, request, current_app, session, title:str, header:list, prefix:str, app:str, link:str, label:str, category:str, overview:str,
                 pag_search:str, pag_type:str="text", btn_type:str="button"):
        self.prefix = prefix
        self.credits = {
            "title":title,
            "header":header,
            "username":session['coach_name'],
            "app":app,
            "user":request.remote_user,
            "addr":request.remote_addr,
            "hostname":current_app.config['HOSTNAME'],
            "created":version.Configs.APP_CREATED,
            "version":version.Configs.APP_VERSION,
            "author":version.Configs.APP_AUTHOR
        }
        ts = current_app.config["TS"]
        if self.credits["user"] is None: self.credits["user"] = "--"
        current_app.logger.info("%s started; Modname=%s; Remote-Addr=%s; Method=%s", title, current_app.name, request.remote_addr, request.method)
        self.today=ts.todaydate()
        self.todaytime=ts.todaytime()
        self.timeformat=self.todaytime.strftime("%Y-%m-%dT%H:%M:%S")
        self.pag_type = pag_type
        self.pag_search = pag_search
        self.btn_type = btn_type
        self.overview = overview
        self.min_date = ts.delta(months=12, sub=True)
        self.max_date = ts.delta(months=12)
        self.javascript = Javascript(prefix, app, self.credits["user"])
        self.javascript.add({'modname':f"/{current_app.name}/", 'today':self.today, 'min_date':self.min_date, 'max_date':self.max_date, 'link_active':link, 'header':header})
        self.javascript.add({'overview_label':label, 'category':category})


class TimeSet:
    def __init__(self, tz:str):
        self.__tzid = tz
        self.__tz = pytz.timezone(tz)
        self.__dt = datetime
    def setRecordunlock(self, value:int):
        self.__recordunlock = value
    def getRecordunlock(self):
        return (self.todaytime() + timedelta(minutes=self.__recordunlock)).strftime("%Y%m%d%H%M%S%f")
    def today(self):
        return self.todaytime().today()
    def todaydate(self):
        return self.todaytime().today().date()
    def todaytime(self) -> datetime:
        return self.__dt.now(tz=self.__tz)
    def todaytime_utc(self) -> datetime:
        return self.__dt.now(tz=pytz.timezone('UTC'))
    def isocalendar(self, ts=None):
        if not ts: ts = self.todaytime()
        return self.__dt.isocalendar(ts)
    def fromtimestamp(self, ts:float):
        return self.__dt.fromtimestamp(timestamp=ts, tz=self.__tz)
    def addtimezone(self, datetime:datetime):
        timestamp_float = datetime.timestamp()
        return self.fromtimestamp(timestamp_float)
    def delta(self, days:int=None, years:int=None, months:int=None, hours:int=None, sub:bool=False) -> datetime.date:
        if days is not None:
            delta = relativedelta(days=days)
        elif hours is not None:
            delta = relativedelta(hours=hours)
        elif months is not None:
            delta = relativedelta(months=months)
        elif years is not None:
            delta = relativedelta(years=years)
        if sub: ret = self.__dt.now().date() - delta
        else: ret = self.__dt.now().date() + delta
        return ret
    def deltatime(self, dt:datetime=None, days:int=None, years:int=None, months:int=None, hours:int=None, sub:bool=False) -> datetime:
        if days is not None:
            delta = relativedelta(days=days)
        elif hours is not None:
            delta = relativedelta(hours=hours)
        elif months is not None:
            delta = relativedelta(months=months)
        elif years is not None:
            delta = relativedelta(years=years)
        if dt is None: dt = self.todaytime()
        if sub: ret = dt - delta
        else: ret = dt + delta
        return ret
    def convert(self, date:str, time_from:str, time_to:str):
        dates = date.split('-')
        times_from = time_from.split(':')
        times_to = time_to.split(':')
        tmfrom = self.__dt(int(dates[0]), int(dates[1]), int(dates[2]), int(times_from[0]), int(times_from[1]), tzinfo=self.__tz)
        tmto = self.__dt(int(dates[0]), int(dates[1]), int(dates[2]), int(times_to[0]), int(times_to[1]), tzinfo=self.__tz)
        # tmfrom_ical = tmfrom.strftime('%Y%m%dT%H%M%S')
        # tmto_ical = tmto.strftime('%Y%m%dT%H%M%S')
        return (tmfrom, tmto, self.__tzid)


def get_config(value:str, is_cookie:bool=False, as_dict:bool=False):
    entry = current_app.config[value]
    if is_cookie: entry = current_app.config['COOKIE_PREFIX'] + entry
    if as_dict: entry = dict(json.loads(entry))
    return entry


def get_session_entry(value:str, is_cookie:bool=False, as_dict:bool=False):
    entry = session[value]
    if is_cookie: entry = current_app.config['COOKIE_PREFIX'] + entry
    if as_dict: entry = dict(json.loads(entry))
    return entry


def checkPermissions(conf):
    usedMods = get_session_entry('authMods', as_dict=True)
    valid_mod = 0
    if conf.prefix in usedMods: valid_mod = usedMods[conf.prefix][1]
    conf.javascript.add({'valid_Mod':valid_mod})


def get_db():
    try:
        pool=current_app.config["DB_POOL"]
        if pool is not None:
            db = pool.get_connection()
            if 'DB_ID' not in g:
                g.setdefault('DB_ID', {})
            db_id = g.get('DB_ID')
            if db.connection_id not in db_id:
                db_id[db.connection_id] = db
            current_app.logger.debug("Create Connection of Pool: %s, ID=%s, Count=%s, Max=%s, Size=%s, Reset=%s", pool.pool_name, db.connection_id, pool.connection_count, pool.max_size, pool.pool_size, pool.pool_reset_connection)
        else:
            db = None
    except mariadb.Error as e:
        db = None
        current_app.logger.critical("Error opening connection from pool: %s", e)

    return db


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    try:
        if not app.config["DB_POOL"]:
            config_pool = {
                "pool_name":app.name,
                "pool_size":30
            }
            config_conn = {
                "user":credentials.Passwords.MYSQL_USER,
                "password":credentials.Passwords.MYSQL_PWD,
                "unix_socket":"/run/mysqld/mysqld.sock",
                "host":"localhost",
                "database":"bv",
                "autocommit":False
            }
            pool = mariadb.ConnectionPool(**config_pool, **config_conn)
            app.logger.info("Created Pool: Name=%s, connection_count=%s", pool.pool_name, pool.connection_count)
            app.config.update({"DB_POOL":pool})
            db = pool.get_connection()
            if not db:
                raise mariadb.PoolError("Fehler bei get_connection().")
            cur = db.cursor()
            """ Einlesen Konfigurations-Elemente aus der Datenbanktabelle _Config """
            cur.execute("select item,value from _Config order by item")
            app.config.update(cur.fetchall())
            cur.close()
            db.close()
            rc = "OK"
    except mariadb.PoolError as err:
        app.logger.critical("Pool-Fehler: Anlegen Pool nicht möglich:  %s", err)
        rc = "ERR"
    except mariadb.Error as err:
        app.logger.critical("Datenbank-Fehler: %s", err)
        rc = "ERR"

    return rc
