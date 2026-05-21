import mariadb, sys
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request, session

from .ax_default import mx_get_overview, mx_submit_release
from .db import get_db
from . import version

bp = Blueprint("ax_coaches", __name__)


@bp.route("/ax-get-coaches-edit/", methods=['POST'])
def ax_get_coaches_edit():
    result = request.get_json()
    result_map = dict(result)
    coache_id = result_map["main-id"]
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
            if timestamp_P is not None and item_id_head != coache_id:
                """ Vorherige Berater-ID entsperren """
                cur.execute("update tBerater set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für Berater=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute("UPDATE tBerater SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, coache_id))
        db.commit()
        cur.execute("SELECT id,sperre,Nachname,Vorname,IFNULL(EMail,'') as EMail,IFNULL(Telefon,'') as Telefon,IFNULL(Mobil,'') as Mobil, \
                    IF(Aktiv=TRUE,TRUE,FALSE) as Aktiv,authMods \
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

        cur.close()
        db.close()
    except mariadb.PoolError as err:
        current_app.logger.error("Pool-Fehler: %s/ax-get-coaches-edit/%s/%s", bp.name, coache_id, err)
        dbdata.update({"status":"ERR"})
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-coaches-edit/%s/%s", bp.name, coache_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-get-coaches-overview/", methods=['POST'])
def ax_get_coaches_overview():
    rc_code = mx_get_overview(request, current_app, html_template_body="verwBerater_body.html", 
                              sql=["SELECT a.id,Vorname,Nachname,IFNULL(Telefon,'--') as Telefon,IFNULL(EMail,'--') as EMail,IFNULL(Mobil,'--') as Mobil,IF(Aktiv=TRUE,'✓','') as Aktiv from tBerater a ", 
                                   "ORDER BY a.Vorname, a.Nachname"], search_field=["Vorname", "Nachname"])
    return rc_code


@bp.route("/ax-submit-coaches-release/", methods=['POST'])
def ax_submit_coaches_release():
    rc_code = mx_submit_release(request, current_app, table_name="tBerater")
    return rc_code


@bp.route("/ax-submit-coaches/", methods=['POST'])
def ax_submit_coaches():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "id":"(Neu)", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    valid_mod = session['valid_mod']
    if not valid_mod:
        rc_code['status'] = 'NOPERMISSION'
        return rc_code
    changeUser = session['login_name']

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
            elif pkey == "aktiv":
                berater_aktiv = parm
            elif pkey == "used-modules":
                used_modules = parm
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
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tBerater WHERE id=? FOR UPDATE", (item_id,))
                row_data = cur.fetchone()
                timestamp = str(row_data["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tBerater set sperre=null,Nachname=?,Vorname=?,EMail=NULLIF(?,''),Telefon=?,Mobil=NULLIF(?,''),Aktiv=?, authMods=?, AnlageUser=?,AnlageDatum=current_timestamp() where id=?", 
                                (berater_nachname, berater_vorname, berater_email, berater_telefon, berater_mobil, berater_aktiv, used_modules, changeUser, item_id))
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
            else:
                cur.execute("insert into tBerater(Nachname,Vorname,EMail,Telefon,Mobil,Aktiv,authMods,AnlageUser) values(?,?,NULLIF(?,''),?,NULLIF(?,''),?,?,?)", 
                            (berater_nachname, berater_vorname, berater_email, berater_telefon, berater_mobil, berater_aktiv, used_modules, changeUser))
                last_id = cur.lastrowid
                rc_code["id"] = last_id

            if update_allowed:
                if item_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Name=%s %s", last_id, berater_vorname, berater_nachname)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Name=%s %s", last_id, berater_vorname, berater_nachname)
                    rc_code["mode"] = "INS"
            db.commit()
            cur.close()
            db.close()
        except mariadb.PoolError as err:
            current_app.logger.error("Pool-Fehler: %s/ax-submit-coaches/%s", bp.name, err)
            rc_code["status"] = "ERR"
        except mariadb.IntegrityError as err:
            rc_code["status"] = "DBL"
            current_app.logger.warning("Datenbank-doppelter Eintrag: %s/ax-submit-coaches/%s", bp.name, err)
            db.rollback()
            db.close()
            current_app.logger.warning("Datenbank-Rollback-doppelter Eintrag")
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-coaches/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
