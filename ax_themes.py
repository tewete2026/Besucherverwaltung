import mariadb, sys
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request

from .ax_default import mx_get_overview, mx_submit_release
from .db import get_db
from . import version

bp = Blueprint("ax_themes", __name__, url_prefix=f"/{version.Configs.APP_NAME}")


@bp.route("/ax-get-theme-edit/", methods=['POST'])
def ax_get_theme_edit():
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
                """ Vorherige Themen-ID entsperren """
                cur.execute("update tThemen set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für Themen=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute("UPDATE tThemen SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, main_id))
        db.commit()
        cur.execute("SELECT id,sperre,Thema as bezeichnung FROM tThemen WHERE id=?", (main_id,))
        dbdata.update({"theme":cur.fetchone()})

        act_timestamp = str(dbdata["theme"]["sperre"])
        if act_timestamp == timestamp_N:
            dbdata.update({"timestamp":timestamp_N})
            current_app.logger.debug("Neue Sperre=%s für Thema=%s eingerichtet.", timestamp_N, main_id)
        elif timestamp_P is not None and act_timestamp == timestamp_P:
            dbdata.update({"timestamp":timestamp_P})
        else:
            dbdata.update({"status":"LCK"})

        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-theme-edit/%s/%s", bp.name, main_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-get-theme-overview/", methods=['POST'])
def ax_get_theme_overview():
    rc_code = mx_get_overview(request, current_app, html_template_body="verwThemen_body.html", 
                              sql=["SELECT a.id,a.Thema as bezeichnung from tThemen a", "ORDER BY a.Thema"], search_field=["a.Thema"])
    return rc_code


@bp.route("/ax-submit-theme-release/", methods=['POST'])
def ax_submit_theme_release():
    rc_code = mx_submit_release(request, current_app, table_name="tThemen")
    return rc_code


@bp.route("/ax-submit-theme/", methods=['POST'])
def ax_submit_theme():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "id":"(Neu)", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}

    try:
        item_id = None
        item_timestamp = None
        for pkey, parm in result:
            if pkey == "bezeichnung":
                theme_bezeichnung = parm
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
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tThemen WHERE id=? FOR UPDATE", (item_id,))
                row_data = cur.fetchone()
                timestamp = str(row_data["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tThemen set sperre=null,Thema=? where id=?", (theme_bezeichnung, item_id))
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
            else:
                cur.execute("insert into tThemen(Thema) values(?)", (theme_bezeichnung,))
                last_id = cur.lastrowid
                rc_code["id"] = last_id

            if update_allowed:
                if item_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Bezeichnung=%s", last_id, theme_bezeichnung)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Bezeichnung=%s", last_id, theme_bezeichnung)
                    rc_code["mode"] = "INS"
            db.commit()
            cur.close()
            db.close()
        except mariadb.IntegrityError as err:
            rc_code["status"] = "DBL"
            current_app.logger.warning("Datenbank-doppelter Eintrag: %s/ax-submit-theme/%s", bp.name, err)
            db.rollback()
            db.close()
            current_app.logger.warning("Datenbank-Rollback-doppelter Eintrag")
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-theme/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
