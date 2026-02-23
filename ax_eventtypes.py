import mariadb
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request
import sys

from .db import get_db
from . import version

bp = Blueprint("ax_eventtypes", __name__, url_prefix=f"/{version.Configs.APP_NAME}")


@bp.route("/ax-get-veransttyp-edit/", methods=['POST'])
def ax_get_veransttyp_edit():
    result = request.get_json()
    result_map = dict(result)
    main_id = result_map["main-id"]
    ts = current_app.config["TS"]
    timestamp_N = ts.getRecordunlock()
    timestamp_P = None
    item_id_head = None
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
                """ Vorherige VeranstTyp-ID entsperren """
                cur.execute("update tVeranstTyp set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für VeranstTyp=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute("UPDATE tVeranstTyp SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, main_id))
        db.commit()
        cur.execute("SELECT id,sperre,Bezeichnung FROM tVeranstTyp WHERE id=?", (main_id,))
        dbdata.update({"veransttyp":cur.fetchone()})

        act_timestamp = str(dbdata["veransttyp"]["sperre"])
        if act_timestamp == timestamp_N:
            dbdata.update({"timestamp":timestamp_N})
            current_app.logger.debug("Neue Sperre=%s für VeranstTyp=%s eingerichtet.", timestamp_N, main_id)
        elif timestamp_P is not None and act_timestamp == timestamp_P:
            dbdata.update({"timestamp":timestamp_P})
        else:
            dbdata.update({"status":"LCK"})

        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-veransttyp-edit/%s/%s", bp.name, main_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-get-veransttyp-overview/", methods=['POST'])
def ax_get_veransttyp_overview():
    result_map = dict(request.get_json())
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    overview_search = result_map["overview-search"]
    overview_page = int(result_map["overview-page"])
    overview_maxlines = int(current_app.config["max-line-overview"])
    overview_offset = (overview_page - 1) * overview_maxlines
    overview_readlines = overview_maxlines + 1

    sql_parms = ""
    if overview_search is not None and len(overview_search) > 0 and overview_search != "ALL":
        if overview_search.isnumeric():
            sql_parms = f"WHERE a.id={overview_search}"
        elif not overview_search.isspace():
            search_like = "'%" +  overview_search + "%'"
            sql_parms = f"WHERE a.Bezeichnung like {search_like}"

    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        is_more_lines = False

        cur.execute(f"SELECT a.id,a.Bezeichnung from tVeranstTyp a \
                    {sql_parms} \
                    ORDER BY a.Bezeichnung LIMIT {overview_offset}, {overview_readlines}")
        dbdata.update({"types":cur.fetchall()})
        len_vis = len(dbdata["types"])
        show_lines = len_vis
        if len_vis > overview_maxlines:
            show_lines = overview_maxlines
            is_more_lines = True
            
        rc_code["html"] = render_template("verwVeranstTyp_body.html", types=dbdata["types"][0:show_lines])
        rc_code["pagination"] = is_more_lines
        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-veransttyp-release/", methods=['POST'])
def ax_submit_veransttyp_release():
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
                cur.execute("SELECT IFNULL(sperre,'IGNORE') as sperre FROM tVeranstTyp WHERE id=? FOR UPDATE", (item_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tVeranstTyp set sperre=null where id=? and sperre=?", (item_id, item_timestamp))
                    current_app.logger.debug("RELEASE: Timestamp entfernt. Id=%s, Timestamp=%s, RowCount=%s, Warnings=%s", item_id, item_timestamp, cur.rowcount, cur.warnings)
                else:
                    rc_code["status"] = "IGNORE"
            db.commit()
            cur.close()
            db.close()
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-veransttyp-release/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-veransttyp/", methods=['POST'])
def ax_submit_veransttyp():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "id":"(Neu)", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}

    try:
        item_id = None
        item_timestamp = None
        for pkey, parm in result:
            if pkey == "bezeichnung":
                type_bezeichnung = parm
            elif pkey == "main-id":
                item_id = parm
            elif pkey == "item-timestamp":
                item_timestamp = parm

        try:
            db = get_db()
            if not db:
                raise mariadb.PoolError("Kein Pool gesetzt.")
            db.begin()
            cur = db.cursor(dictionary=True)

            update_allowed = True
            if item_id is not None:
                rc_code["id"] = item_id
                last_id = item_id
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tVeranstTyp WHERE id=? FOR UPDATE", (item_id,))
                row_data = cur.fetchone()
                timestamp = str(row_data["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tVeranstTyp set sperre=null,Bezeichnung=? where id=?", (type_bezeichnung, item_id))
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
            else:
                cur.execute("insert into tVeranstTyp(Bezeichnung) values(?)", (type_bezeichnung,))
                last_id = cur.lastrowid
                rc_code["id"] = last_id

            if update_allowed:
                if item_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Bezeichnung=%s", last_id, type_bezeichnung)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Bezeichnung=%s", last_id, type_bezeichnung)
                    rc_code["mode"] = "INS"
            db.commit()
            cur.close()
            db.close()
        except mariadb.IntegrityError as err:
            rc_code["status"] = "DBL"
            current_app.logger.warning("Datenbank-doppelter Eintrag: %s/ax-submit-veransttyp/%s", bp.name, err)
            db.rollback()
            db.close()
            current_app.logger.warning("Datenbank-Rollback-doppelter Eintrag")
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-veransttyp/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
