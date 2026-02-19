import mariadb
from datetime import datetime, timedelta
import pytz
from flask import current_app
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
    def __init__(self, request, current_app, title:str, header:list, prefix:str, app:str, link:str, label:str, category:str, overview:str,
                 pag_search:str, pag_type:str="text", btn_type:str="button"):
        self.credits = {
            "title":title,
            "header":header,
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
        self.today=ts.today()
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
    def todaytime(self):
        return self.__dt.now(tz=self.__tz)
    def isocalendar(self, ts=None):
        if not ts: ts = self.todaytime()
        return self.__dt.isocalendar(ts)
    def fromtimestamp(self, ts:float):
        return self.__dt.fromtimestamp(timestamp=ts, tz=self.__tz)
    def addtimezone(self, datetime:datetime):
        timestamp_float = datetime.timestamp()
        return self.fromtimestamp(timestamp_float)
    def delta(self, days:int=None, years:int=None, months:int=None, sub:bool=False) -> datetime:
        if days is not None:
            delta = relativedelta(days=days)
        elif months is not None:
            delta = relativedelta(months=months)
        elif years is not None:
            delta = relativedelta(years=years)
        if sub: ret = self.__dt.now() - delta
        else: ret = self.__dt.now() + delta
        return ret
        

def get_db():
    try:
        pool=current_app.config["DB_POOL"]
        if pool is not None:
            db = pool.get_connection()
            current_app.logger.debug("Create Connection von Pool: %s, ID=%s", pool.pool_name, db.connection_id)
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
                "pool_size":20
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
            app.logger.debug("Created Pool: Name=%s, connection_count=%s", pool.pool_name, pool.connection_count)
            app.config.update({"DB_POOL":pool})
            db = pool.get_connection()
            if not db:
                raise mariadb.PoolError("Fehler bei get_connection().")
            cur = db.cursor()
            """ Einlesen Konfigurations-Elemente aus der Datenbanktabelle _Config """
            cur.execute("select item,value from _Config order by id")
            app.config.update(cur.fetchall())
            cur.close()
            db.close()
            rc = "OK"
    except mariadb.Error as err:
        app.logger.critical("Anlegen Pool nicht möglich!")
        rc = "ERR"

    return rc
