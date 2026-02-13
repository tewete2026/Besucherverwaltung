import mariadb
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request
from datetime import datetime
from datetime import timedelta
import sys

from .db import get_db
from . import version
from . import tools

bp = Blueprint("ax_targets", __name__, url_prefix=f"/{version.Configs.APP_NAME}")


@bp.route("/ax-get-targets-edit/", methods=['POST'])
def ax_get_targets_edit():
    result = request.get_json()
    result_map = dict(result)
    target_id = result_map["main-id"]
    timestamp_N = tools.getTS(current_app.config)
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
            if timestamp_P is not None and item_id_head != target_id:
                """ Vorherige Orte-ID entsperren """
                cur.execute("update tOrte set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für Orte=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute("UPDATE tOrte SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, target_id))
        db.commit()
        cur.execute("SELECT id,sperre,Bezeichnung,IFNULL(MaxBesucher,'') as MaxBesucher FROM tOrte WHERE id=?", (target_id,))
        dbdata.update({"target":cur.fetchone()})

        act_timestamp = str(dbdata["target"]["sperre"])
        if act_timestamp == timestamp_N:
            dbdata.update({"timestamp":timestamp_N})
            current_app.logger.debug("Neue Sperre=%s für Ort=%s eingerichtet.", timestamp_N, target_id)
        elif timestamp_P is not None and act_timestamp == timestamp_P:
            dbdata.update({"timestamp":timestamp_P})
        else:
            dbdata.update({"status":"LCK"})

        cur.execute("SELECT id,IFNULL(Bezeichnung,'--') as Bezeichnung,DATE_FORMAT(DATE(Datum),'%d.%m.%Y') as datum \
                    FROM tVeranst WHERE Ort=? ORDER BY Bezeichnung", (target_id,))
        dbdata.update({"events":cur.fetchall()})

        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-targets-edit/%s/%s", bp.name, target_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-get-targets-overview/", methods=['POST'])
def ax_get_targets_overview():
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
            sql_parms = f"WHERE id={overview_search}"
        elif not overview_search.isspace():
            search_like = "'%" +  overview_search + "%'"
            sql_parms = f"WHERE bezeichnung like {search_like}"

    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        is_more_lines = False

        cur.execute(f"SELECT a.id,a.Bezeichnung,IFNULL(a.MaxBesucher,'--') as MaxBesucher,IFNULL(c.anzahl_veranst,'--') as anzahl_veranst from tOrte a \
                    left join (select Ort,count(id) as anzahl_veranst from tVeranst group by Ort) c on c.Ort=a.id \
                    {sql_parms} \
                    ORDER BY a.Bezeichnung LIMIT {overview_offset}, {overview_readlines}")
        dbdata.update({"targets":cur.fetchall()})
        len_vis = len(dbdata["targets"])
        show_lines = len_vis
        if len_vis > overview_maxlines:
            show_lines = overview_maxlines
            is_more_lines = True
            
        rc_code["html"] = render_template("verwOrte_body.html", targets=dbdata["targets"][0:show_lines])
        rc_code["pagination"] = is_more_lines
        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-targets-release/", methods=['POST'])
def ax_submit_targets_release():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    try:
        orte_id = None
        item_timestamp = None
        for pkey, parm in result:
            if pkey == "item-id":
                orte_id = parm
            elif pkey == "item-timestamp":
                item_timestamp = parm
        try:
            db = get_db()
            if not db:
                raise mariadb.PoolError()
            db.begin()
            cur = db.cursor(dictionary=True)

            if orte_id is not None:
                rc_code["id"] = orte_id
                cur.execute("SELECT IFNULL(sperre,'IGNORE') as sperre FROM tOrte WHERE id=? FOR UPDATE", (orte_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tOrte set sperre=null where id=? and sperre=?", (orte_id, item_timestamp))
                    current_app.logger.debug("RELEASE: Timestamp entfernt. Id=%s, Timestamp=%s, RowCount=%s, Warnings=%s", orte_id, item_timestamp, cur.rowcount, cur.warnings)
                else:
                    rc_code["status"] = "IGNORE"
            db.commit()
            cur.close()
            db.close()
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-targets-release/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-targets/", methods=['POST'])
def ax_submit_targets():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "id":"(Neu)", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}

    try:
        item_id = None
        item_timestamp = None
        events_remove = None
        for pkey, parm in result:
            if pkey == "bezeichnung":
                bezeichnung = parm
            elif pkey == "maxbesucher":
                maxbesucher = parm
            elif pkey == "veranst-remove":
                events_remove = parm
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
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tOrte WHERE id=? FOR UPDATE", (item_id,))
                row_data = cur.fetchone()
                timestamp = str(row_data["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tOrte set sperre=null,Bezeichnung=?,MaxBesucher=NULLIF(?,'') where id=?", (bezeichnung, maxbesucher, item_id))
                    if len(events_remove) > 0:
                        remove_verId = []
                        remove_rowId = []
                        for verId, rowId in events_remove:
                            remove_verId.append(verId)
                            remove_rowId.append(rowId)
                        search = ",".join(remove_rowId)
                        cur.execute(f"update tVeranst set Ort=null where id in ({search})")
                        current_app.logger.debug("Entfernt ID=%s aus tVeranst für Ort=%s: RowCount=%s, Warnings=%s", search, item_id, cur.rowcount, cur.warnings)
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
            else:
                cur.execute("insert into tOrte(Bezeichnung,MaxBesucher) values(?,NULLIF(?,''))", (bezeichnung, maxbesucher))
                last_id = cur.lastrowid
                rc_code["id"] = last_id

            if update_allowed:
                if item_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Name=%s", last_id, bezeichnung)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Name=%s", last_id, bezeichnung)
                    rc_code["mode"] = "INS"
            db.commit()
            cur.close()
            db.close()
        except mariadb.IntegrityError as err:
            rc_code["status"] = "DBL"
            current_app.logger.warning("Datenbank-doppelter Eintrag: %s/ax-submit-targets/%s", bp.name, err)
            db.rollback()
            db.close()
            current_app.logger.warning("Datenbank-Rollback-doppelter Eintrag")
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-targets/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
