import mariadb, re, sys
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request

from .db import get_db
from . import version

bp = Blueprint("ax_default", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.route("/ax-up-error-msg/", methods=['POST'])
def ax_up_error_msg():
    result = request.get_json()
    current_app.logger.debug("Empfangene JavaScript-Meldungen: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    if "alert" in result:
        for err_text in result["alert"]:
            current_app.logger.error("Javascript-Fehlermeldung: %s",err_text)
    if "init" in result:
        for err_text in result["init"]:
            current_app.logger.debug("Init-Meldung: %s",err_text)
    if "init_err" in result:
        for err_text in result["init_err"]:
            current_app.logger.error("Init-Error-Meldung: %s",err_text)
    return rc_code


def mx_get_overview(request, current_app, **kwargs):
    search_field = kwargs['search_field']
    sql = kwargs['sql']
    html_template = kwargs['html_template_body']
    primary="id"
    if "primary" in kwargs:
        primary=kwargs['primary']


    result_map = dict(request.get_json())
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    overview_search = result_map["overview-search"]
    overview_page = int(result_map["overview-page"])
    overview_maxlines = int(current_app.config["max-line-overview"])
    overview_offset = (overview_page - 1) * overview_maxlines
    overview_readlines = overview_maxlines + 1

    sql_parms = ""
    if overview_search is not None and len(overview_search) > 0 and overview_search != "ALL":
        if re.match(r"[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}", overview_search):
            sql_parms = f"WHERE {search_field[0]}<='{overview_search}'"
        elif overview_search.isnumeric():
            sql_parms = f"WHERE a.{primary}={overview_search}"
        elif not overview_search.isspace():
            search_like = "'%" +  overview_search + "%'"
            sql_parms = f"WHERE {search_field[0]} like {search_like}"
            if len(search_field) > 1:
                sql_parms += f" or {search_field[1]} like {search_like}"

    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        is_more_lines = False

        cur.execute(f'{sql[0]} {sql_parms} {sql[1]} LIMIT {overview_offset}, {overview_readlines}')
        dbdata.update({"entries":cur.fetchall()})
        len_vis = len(dbdata["entries"])
        show_lines = len_vis
        if len_vis > overview_maxlines:
            show_lines = overview_maxlines
            is_more_lines = True
            
        rc_code["html"] = render_template(html_template, entries=dbdata["entries"][0:show_lines])
        rc_code["pagination"] = is_more_lines
        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/mx_get_overview/%s", bp.name, err)
        rc_code["status"] = "ERR"

    return rc_code


def mx_submit_release(request, current_app, **kwargs):
    table_name = kwargs['table_name']
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    try:
        item_id = None
        item_timestamp = None
        for pkey, parm in result:
            if pkey == "item-id":
                item_id = parm
            elif pkey == "item-timestamp":
                item_timestamp = parm
        try:
            db = get_db()
            if not db:
                raise mariadb.PoolError()
            db.begin()
            cur = db.cursor(dictionary=True)

            if item_id is not None:
                rc_code["id"] = item_id
                cur.execute(f"SELECT IFNULL(sperre,'IGNORE') as sperre FROM {table_name} WHERE id=? FOR UPDATE", (item_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == item_timestamp:
                    cur.execute(f"update {table_name} set sperre=null where id=? and sperre=?", (item_id, item_timestamp))
                    current_app.logger.debug("RELEASE: Timestamp in %s entfernt. Id=%s, Timestamp=%s, RowCount=%s, Warnings=%s", table_name, item_id, item_timestamp, cur.rowcount, cur.warnings)
                else:
                    rc_code["status"] = "IGNORE"
            db.commit()
            cur.close()
            db.close()
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/mx_submit_release/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code


def mx_get_edit(request, current_app, **kwargs):
    table_name = kwargs['table_name']
    data_key = kwargs['data_key']
    select_field = kwargs['select_field']
    result = request.get_json()
    result_map = dict(result)
    main_id = result_map["main-id"]
    ts = current_app.config["TS"]
    timestamp_N = ts.getRecordunlock()
    timestamp_P = None

    dbdata={}
    try:
        dbdata.update({"status":"OK"})
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        db.begin()
        cur = db.cursor(dictionary=True)
        
        if "timestamp" in result_map:
            timestamp_P = result_map["timestamp"]
        if "item_id_head" in result_map:
            item_id_head = result_map["item_id_head"]
            if timestamp_P is not None and item_id_head != main_id:
                """ Vorherige ID entsperren """
                cur.execute(f"update {table_name} set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für ID=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute(f"UPDATE {table_name} SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, main_id))
        db.commit()
        cur.execute(f"SELECT id,sperre,{select_field} FROM {table_name} WHERE id=?", (main_id,))
        dbdata.update({data_key:cur.fetchone()})

        act_timestamp = str(dbdata[data_key]["sperre"])
        if act_timestamp == timestamp_N:
            dbdata.update({"timestamp":timestamp_N})
            current_app.logger.debug("Neue Sperre=%s für ID=%s eingerichtet.", timestamp_N, main_id)
        elif timestamp_P is not None and act_timestamp == timestamp_P:
            dbdata.update({"timestamp":timestamp_P})
        else:
            dbdata.update({"status":"LCK"})

        if 'queries' in kwargs:
            queries = kwargs['queries']
            for key, item in queries.items():
                cur.execute(item['sql'], (main_id,))
                dbdata.update({key:cur.fetchall()})

        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-edit/%s/%s", bp.name, main_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata
