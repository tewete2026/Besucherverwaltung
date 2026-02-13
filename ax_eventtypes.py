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

bp = Blueprint("ax_eventtypes", __name__, url_prefix=f"/{version.Configs.APP_NAME}")


@bp.route("/ax-get-coache-edit/", methods=['POST'])
def ax_get_coache_edit():
    result = request.get_json()
    result_map = dict(result)
    coache_id = result_map["coache-id"]
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
            if timestamp_P is not None and item_id_head != coache_id:
                """ Vorherige Berater-ID entsperren """
                cur.execute("update tBerater set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für Berater=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute("UPDATE tBerater SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, coache_id))
        db.commit()
        cur.execute("SELECT id,sperre,Nachname,Vorname,IFNULL(EMail,'') as EMail,Telefon,IFNULL(Mobil,'') as Mobil,\
                    IF(Aktiv=TRUE,TRUE,FALSE) as Aktiv,IF(TdM=TRUE,TRUE,FALSE) as TdM,IF(BerExt=TRUE,TRUE,FALSE) as BerExt \
                    FROM tBerater WHERE id=?", (coache_id,))
        dbdata.update({"coache":cur.fetchone()})

        act_timestamp = str(dbdata["coache"]["sperre"])
        if act_timestamp == timestamp_N:
            dbdata.update({"timestamp":timestamp_N})
            current_app.logger.debug("Neue Sperre=%s für Berater=%s eingerichtet.", timestamp_N, coache_id)
        elif timestamp_P is not None and act_timestamp == timestamp_P:
            dbdata.update({"timestamp":timestamp_P})
        else:
            dbdata.update({"status":"LCK"})
        
        cur.execute("SELECT id,ThemenID FROM tBeraterthem WHERE BeraterID=?", (coache_id,))
        dbdata.update({"coached_themes":cur.fetchall()})
        
        cur.execute("SELECT id,ThemenID FROM tBeraterInfo WHERE BeraterID=?", (coache_id,))
        dbdata.update({"info_themes":cur.fetchall()})
        
        cur.execute("SELECT id,GeraeteID FROM tBeraterGer WHERE BeraterID=?", (coache_id,))
        dbdata.update({"coached_devices":cur.fetchall()})

        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-coache-edit/%s/%s", bp.name, coache_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-get-coaches-overview/", methods=['POST'])
def ax_get_coaches_overview():
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
            sql_parms = f"WHERE (vorname like {search_like} or nachname like {search_like})"

    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        is_more_lines = False

        cur.execute(f"SELECT a.id,Vorname,Nachname,IF(Telefon='','--',Telefon) as Telefon,IFNULL(EMail,'--') as EMail,IFNULL(Mobil,'--') as Mobil,IF(Aktiv=TRUE,'**','-') as Aktiv \
                    from tBerater a \
                    {sql_parms} \
                    ORDER BY a.Nachname, a.Vorname LIMIT {overview_offset}, {overview_readlines}")
        dbdata.update({"coaches":cur.fetchall()})
        len_vis = len(dbdata["coaches"])
        show_lines = len_vis
        if len_vis > overview_maxlines:
            show_lines = overview_maxlines
            is_more_lines = True
            
        rc_code["html"] = render_template("verwBerater_body.html", coaches=dbdata["coaches"][0:show_lines])
        rc_code["pagination"] = is_more_lines
        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-berater-release/", methods=['POST'])
def ax_submit_berater_release():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    try:
        berater_id = None
        berater_timestamp = None
        for pkey, parm in result:
            if pkey == "item-id":
                berater_id = parm
            elif pkey == "item-timestamp":
                berater_timestamp = parm
        try:
            db = get_db()
            if not db:
                raise mariadb.PoolError()
            db.begin()
            cur = db.cursor(dictionary=True)

            if berater_id is not None:
                rc_code["id"] = berater_id
                cur.execute("SELECT IFNULL(sperre,'IGNORE') as sperre FROM tBerater WHERE id=? FOR UPDATE", (berater_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == berater_timestamp:
                    cur.execute("update tBerater set sperre=null where id=? and sperre=?", (berater_id, berater_timestamp))
                    current_app.logger.debug("RELEASE: Timestamp entfernt. Id=%s, Timestamp=%s, RowCount=%s, Warnings=%s", berater_id, berater_timestamp, cur.rowcount, cur.warnings)
                else:
                    rc_code["status"] = "IGNORE"
            db.commit()
            cur.close()
            db.close()
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-berater-release/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-berater/", methods=['POST'])
def ax_submit_berater():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "id":"(Neu)", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}

    try:
        item_id = None
        item_timestamp = None
        for pkey, parm in result:
            if pkey == "vorname":
                berater_vorname = parm
            elif pkey == "nachname":
                berater_nachname = parm
            elif pkey == "email":
                berater_email = parm
            elif pkey == "telefon":
                berater_telefon = parm
            elif pkey == "mobil":
                berater_mobil = parm
            elif pkey == "tdm":
                berater_tdm = parm
            elif pkey == "ext":
                berater_ext = parm
            elif pkey == "aktiv":
                berater_aktiv = parm
            elif pkey == "coached-themes":
                coached_themes = parm
            elif pkey == "info-themes":
                info_themes = parm
            elif pkey == "coached-devices":
                coached_devices = parm
            elif pkey == "item-id":
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
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tBerater WHERE id=? FOR UPDATE", (item_id,))
                row_data = cur.fetchone()
                timestamp = str(row_data["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tBerater set sperre=null,Nachname=?,Vorname=?,EMail=NULLIF(?,''),Telefon=?,Mobil=NULLIF(?,''),Aktiv=?,TdM=?,BerExt=? where id=?", 
                                (berater_nachname, berater_vorname, berater_email, berater_telefon, berater_mobil, berater_aktiv, berater_tdm, berater_ext, item_id))
                    cur.execute("delete from tBeraterGer where BeraterID=?", (item_id,))
                    current_app.logger.debug("Datensätze tBeraterGer gelöscht: BeraterID=%s, Anzahl=%s", item_id, cur.rowcount)
                    cur.execute("delete from tBeraterInfo where BeraterID=?", (item_id,))
                    current_app.logger.debug("Datensätze tBeraterInfo gelöscht: BeraterID=%s, Anzahl=%s", item_id, cur.rowcount)
                    cur.execute("delete from tBeraterthem where BeraterID=?", (item_id,))
                    current_app.logger.debug("Datensätze tBeraterthem gelöscht: BeraterID=%s, Anzahl=%s", item_id, cur.rowcount)
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
            else:
                cur.execute("insert into tBerater(Nachname,Vorname,EMail,Telefon,Mobil,Aktiv,TdM,BerExt) \
                            values(?,?,NULLIF(?,''),?,NULLIF(?,''),?,?,?)", 
                            (berater_nachname, berater_vorname, berater_email, berater_telefon, berater_mobil, berater_aktiv, berater_tdm, berater_ext))
                last_id = cur.lastrowid
                rc_code["id"] = last_id

            if update_allowed:
                for themeId in coached_themes:
                    cur.execute("insert into tBeraterthem(BeraterID,ThemenID) values(?,?)", (last_id, themeId))
                    current_app.logger.debug("Datensätze tBeraterthem hinzugefügt: BeraterID=%s, ThemenID=%s, ID=%s, Anzahl=%s", last_id, themeId, cur.lastrowid, cur.rowcount)
                for themeId in info_themes:
                    cur.execute("insert into tBeraterInfo(BeraterID,ThemenID) values(?,?)", (last_id, themeId))
                    current_app.logger.debug("Datensätze tBeraterInfo hinzugefügt: BeraterID=%s, ThemenID=%s, ID=%s, Anzahl=%s", last_id, themeId, cur.lastrowid, cur.rowcount)
                for devId in coached_devices:
                    cur.execute("insert into tBeraterGer(BeraterID,GeraeteID) values(?,?)", (last_id, devId))
                    current_app.logger.debug("Datensätze tBeraterGer hinzugefügt: BeraterID=%s, GeraeteID=%s, ID=%s, Anzahl=%s", last_id, devId, cur.lastrowid, cur.rowcount)
                if item_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Name=%s %s", last_id, berater_vorname, berater_nachname)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Name=%s %s", last_id, berater_vorname, berater_nachname)
                    rc_code["mode"] = "INS"
            db.commit()
            cur.close()
            db.close()
        except mariadb.IntegrityError as err:
            rc_code["status"] = "DBL"
            current_app.logger.warning("Datenbank-doppelter Eintrag: %s/ax-submit-berater/%s", bp.name, err)
            db.rollback()
            db.close()
            current_app.logger.warning("Datenbank-Rollback-doppelter Eintrag")
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-berater/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
