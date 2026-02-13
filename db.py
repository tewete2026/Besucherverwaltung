import mariadb
from flask import g
from flask import current_app
from datetime import date
from dateutil.relativedelta import relativedelta
from . import version

class Javascript:
    def __init__(self, prefix:str, app:str, user:str):
        if user is None: user = "--"
        self.__outline = "const SERVER_OPTIONS = {'PREFIX':'" + prefix + "', 'APP':'" + app + "', 'USER':'" + user + "'"
    def add(self, attr:dict):
        for key, value in attr.items():
            if isinstance(value, list):
                value = str(value).replace("'", '"')
            elif not isinstance(value, str):
                value = str(value)
            self.__outline += ", '" + key + "':'" + value + "'"
    def getOut(self) -> str:
        return self.__outline + "}"
    
    @staticmethod
    def toOptions(rows:list[dict]) -> str:
        opts = ""
        for elem in rows:
            opts += "<option value=\"" + str(elem["id"]) + "\">" + elem["bezeichnung"] + "</option>"
        return opts
    

class Configure:
    def __init__(self, title:str, header:list, prefix:str, app:str, link:str, label:str, category:str, overview:str, pag_search:str, pag_type:str, request, current_app):
        self.credits = {
            "title":title,
            "header":header,
            "app":app,
            "user":request.remote_user,
            "addr":request.remote_addr,
            "created":version.Configs.APP_CREATED,
            "version":version.Configs.APP_VERSION,
            "author":version.Configs.APP_AUTHOR
        }
        if self.credits["user"] is None: self.credits["user"] = "--"
        current_app.logger.info("%s started; Modname=%s; Remote-Addr=%s; Method=%s", title, current_app.name, request.remote_addr, request.method)
        self.today=date.today()
        self.pag_type = pag_type
        self.pag_search = pag_search
        self.overview = overview
        self.min_date = self.today - relativedelta(months=12)
        self.max_date = self.today + relativedelta(months=12)
        self.javascript = Javascript(prefix, app, self.credits["user"])
        self.javascript.add({'modname':f"/{current_app.name}/", 'today':self.today, 'min_date':self.min_date, 'max_date':self.max_date, 'link_active':link, 'header':header})
        self.javascript.add({'overview_label':label, 'category':category})
        

def get_db():
    try:
        if "db" not in g:
            pool=current_app.config["DB_POOL"]
            g.db = pool.get_connection()
            current_app.logger.debug("Create Connection von Pool: %s, ID=%s", pool.pool_name, g.db.connection_id)
    except mariadb.Error as e:
        g.db = None
        current_app.logger.critical("Error opening connection from pool: %s", e)

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)
    if db is not None:
        current_app.logger.debug("Connection close: %s-%s", db.database, db.connection_id)
        db.close()


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)

    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    try:
        if not app.config["DB_POOL"]:
            config_pool = {
                "pool_name":app.name,
                "pool_size":20
            }
            config_conn = {
                "user":"pcafe",
                "password":"u72ggBa5551",
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
                raise mariadb.PoolError()
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