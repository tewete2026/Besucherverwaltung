import mariadb, sys
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request

from .ax_default import mx_get_overview, mx_submit_release
from .db import get_db
from . import version

bp = Blueprint("ax_targets", __name__, url_prefix=f"/{version.Configs.APP_NAME}")


@bp.route("/ax-get-targets-edit/", methods=['POST'])
def ax_get_targets_edit():
    result = request.get_json()
    result_map = dict(result)
    target_id = result_map["main-id"]
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
    rc_code = mx_get_overview(request, current_app, html_template_body="verwOrte_body.html", 
                              sql=["SELECT a.id,a.Bezeichnung,IFNULL(a.MaxBesucher,'--') as MaxBesucher,IFNULL(c.anzahl_veranst,'--') as anzahl_veranst from tOrte a \
                    left join (select Ort,count(id) as anzahl_veranst from tVeranst group by Ort) c on c.Ort=a.id", 
                    "ORDER BY a.Bezeichnung"], search_field=["a.Bezeichnung"])
    return rc_code


@bp.route("/ax-submit-targets-release/", methods=['POST'])
def ax_submit_targets_release():
    rc_code = mx_submit_release(request, current_app, table_name="tOrte")
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
