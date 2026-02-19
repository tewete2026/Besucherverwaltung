import mariadb
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request
import sys

from .db import get_db
from . import version

bp = Blueprint("ax_devices", __name__, url_prefix=f"/{version.Configs.APP_NAME}")


@bp.route("/ax-get-devices-edit/", methods=['POST'])
def ax_get_devices_edit():
    result = request.get_json()
    result_map = dict(result)
    device_id = result_map["main-id"]
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
            if timestamp_P is not None and item_id_head != device_id:
                """ Vorherige Geräte-ID entsperren """
                cur.execute("update tGeraete set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für Gerät=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute("UPDATE tGeraete SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, device_id))
        db.commit()
        cur.execute("SELECT id,sperre,Bezeichnung FROM tGeraete WHERE id=?", (device_id,))
        dbdata.update({"device":cur.fetchone()})

        act_timestamp = str(dbdata["device"]["sperre"])
        if act_timestamp == timestamp_N:
            dbdata.update({"timestamp":timestamp_N})
            current_app.logger.debug("Neue Sperre=%s für Gerät=%s eingerichtet.", timestamp_N, device_id)
        elif timestamp_P is not None and act_timestamp == timestamp_P:
            dbdata.update({"timestamp":timestamp_P})
        else:
            dbdata.update({"status":"LCK"})
        
        cur.execute("SELECT a.id,a.BeraterID,b.Vorname,b.Nachname,IFNULL(b.Telefon,'--') as Telefon,IFNULL(b.EMail,'--') as EMail FROM tBeraterGer a \
                     join tBerater b on b.id=a.BeraterID \
                     WHERE GeraeteID=? ", (device_id,))
        dbdata.update({"coached_devices":cur.fetchall()})

        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-devices-edit/%s/%s", bp.name, device_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-get-devices-overview/", methods=['POST'])
def ax_get_devices_overview():
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

        cur.execute(f"SELECT a.id,a.Bezeichnung,IFNULL(c.anzahl_berater,'--') as anzahl_berater from tGeraete a \
                    left join (select GeraeteID,count(BeraterID) as anzahl_berater from tBeraterGer group by GeraeteID) c on c.GeraeteID=a.id \
                    {sql_parms} \
                    ORDER BY a.Bezeichnung LIMIT {overview_offset}, {overview_readlines}")
        dbdata.update({"devices":cur.fetchall()})
        len_vis = len(dbdata["devices"])
        show_lines = len_vis
        if len_vis > overview_maxlines:
            show_lines = overview_maxlines
            is_more_lines = True
            
        rc_code["html"] = render_template("verwGeraete_body.html", devices=dbdata["devices"][0:show_lines])
        rc_code["pagination"] = is_more_lines
        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-devices-release/", methods=['POST'])
def ax_submit_devices_release():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    try:
        devices_id = None
        devices_timestamp = None
        for pkey, parm in result:
            if pkey == "item-id":
                devices_id = parm
            elif pkey == "item-timestamp":
                devices_timestamp = parm
        try:
            db = get_db()
            if not db:
                raise mariadb.PoolError()
            db.begin()
            cur = db.cursor(dictionary=True)

            if devices_id is not None:
                rc_code["id"] = devices_id
                cur.execute("SELECT IFNULL(sperre,'IGNORE') as sperre FROM tGeraete WHERE id=? FOR UPDATE", (devices_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == devices_timestamp:
                    cur.execute("update tGeraete set sperre=null where id=? and sperre=?", (devices_id, devices_timestamp))
                    current_app.logger.debug("RELEASE: Timestamp entfernt. Id=%s, Timestamp=%s, RowCount=%s, Warnings=%s", devices_id, devices_timestamp, cur.rowcount, cur.warnings)
                else:
                    rc_code["status"] = "IGNORE"
            db.commit()
            cur.close()
            db.close()
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-devices-release/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-devices/", methods=['POST'])
def ax_submit_devices():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "id":"(Neu)", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}

    try:
        item_id = None
        item_timestamp = None
        coaches_remove = None
        for pkey, parm in result:
            if pkey == "bezeichnung":
                bezeichnung = parm
            elif pkey == "coaches-remove":
                coaches_remove = parm
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
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tGeraete WHERE id=? FOR UPDATE", (item_id,))
                row_data = cur.fetchone()
                timestamp = str(row_data["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tGeraete set sperre=null,Bezeichnung=? where id=?", (bezeichnung, item_id))
                    if len(coaches_remove) > 0:
                        search = ",".join(coaches_remove)
                        cur.execute(f"delete from tBeraterGer where id in ({search})")
                        current_app.logger.debug("Entfernt ID=%s aus tBeraterGer für Gerät=%s: RowCount=%s, Warnings=%s", search, item_id, cur.rowcount, cur.warnings)
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
            else:
                cur.execute("insert into tGeraete(Bezeichnung) values(?)", (bezeichnung,))
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
            current_app.logger.warning("Datenbank-doppelter Eintrag: %s/ax-submit-devices/%s", bp.name, err)
            db.rollback()
            db.close()
            current_app.logger.warning("Datenbank-Rollback-doppelter Eintrag")
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-devices/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
