import mariadb
from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template
from dateutil import parser
import sys

from .db import get_db
from . import version

bp = Blueprint("ax_events", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.route("/ax-get-events-edit/", methods=['POST'])
def ax_get_veranst_edit():
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
                """ Vorherige Besucher-ID entsperren """
                cur.execute("update tVeranst set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für Veranst=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute("UPDATE tVeranst SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, main_id))
        db.commit()
        cur.execute("SELECT id,sperre,typ,IFNULL(ort,-1) as ort,DATE_FORMAT(DATE(datum),'%Y-%m-%d') as datum,von,bis,dauer,IFNULL(thema,-1) as thema \
                    FROM tVeranst WHERE id=?", (main_id,))
        dbdata.update({"veranst":cur.fetchone()})

        act_timestamp = str(dbdata["veranst"]["sperre"])
        if act_timestamp == timestamp_N:
            dbdata.update({"timestamp":timestamp_N})
            current_app.logger.debug("Neue Sperre=%s für Veranst=%s eingerichtet.", timestamp_N, main_id)
        elif timestamp_P is not None and act_timestamp == timestamp_P:
            dbdata.update({"timestamp":timestamp_P})
        else:
            dbdata.update({"status":"LCK"})

        cur.execute("SELECT id,BeraterID FROM tBeraterVer WHERE VeranstID=?", (main_id,))
        dbdata.update({"berater":cur.fetchall()})
        cur.execute("SELECT id,BesucherID,IFNULL(ThemenID,-1) as ThemenID,IFNULL(GeraeteID,-1) as GeraeteID,spende,IF(BesucherWL=true,true,false) as BesucherWL \
                    FROM tBesuche WHERE VeranstID=?", (main_id,))
        dbdata.update({"besucher":cur.fetchall()})
        
        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-veranst-edit/%s/%s", bp.name, main_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-check-veranstort/", methods=['POST'])
def ax_submit_check_veranstort():
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    result = request.get_json()
    result_map = dict(result)
    veranst_id = result_map["veranst-id"]

    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)

        sql_base = "select id from tVeranst where Datum=? and Ort=? and not (Bis<? or Von>?"
        if veranst_id is None:
            sql_cmd = sql_base + ")"
            parms = (result_map["datum"], result_map["ort"], result_map["von"], result_map["bis"])
        else:
            sql_cmd = sql_base + " or id=?)"
            parms = (result_map["datum"], result_map["ort"], result_map["von"], result_map["bis"], veranst_id)

        cur.execute(sql_cmd, parms)

        if cur.rowcount > 0:
            rc_code["is_invalid"] = "YES"

        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbankfehler: ax-check-veranstort= %s", err)
        rc_code["status"] = "ERR"
        db.close()
    
    return rc_code


@bp.route("/ax-get-events-overview/", methods=['POST'])
def ax_get_events_overview():
    result_map = dict(request.get_json())
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    overview_search = result_map["overview-search"]
    overview_page = int(result_map["overview-page"])
    overview_maxlines = int(current_app.config["max-line-overview"])
    overview_offset = (overview_page - 1) * overview_maxlines
    overview_readlines = overview_maxlines + 1

    sql_parms = ""
    if overview_search is not None and len(overview_search) > 0 and overview_search != "ALL":
        if not overview_search.isspace():
            sql_parms = f"WHERE Datum<='{overview_search}'"

    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        is_more_lines = False

        cur.execute(f"SELECT a.id,DATE_FORMAT(DATE(a.datum),'%d.%m.%Y') as datum,a.bezeichnung,IFNULL(d.MaxBesucher,'--') as plaetze,IFNULL(b.anzahl,'--') as anzahl_s,IFNULL(c.anzahl,'--') as anzahl_b \
                    from tVeranst a \
                    left join (select count(BesucherID) as anzahl,VeranstID from tBesuche group by VeranstID) b ON (b.VeranstID=a.id) \
                    left join (select count(BeraterID) as anzahl,VeranstID from tBeraterVer group by VeranstID) c on (c.VeranstID=a.id) \
                    left join tOrte d on (a.Ort=d.id) \
                    {sql_parms} \
                    ORDER BY a.datum desc, a.id desc LIMIT {overview_offset}, {overview_readlines}")
        dbdata.update({"events":cur.fetchall()})
        len_vis = len(dbdata["events"])
        show_lines = len_vis
        if len_vis > overview_maxlines:
            show_lines = overview_maxlines
            is_more_lines = True
            
        rc_code["html"] = render_template("index_body.html", events=dbdata["events"][0:show_lines])
        rc_code["pagination"] = is_more_lines
        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-events/", methods=['POST'])
def ax_submit_veranst():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    berater = []
    besucher = {}
    ts = current_app.config["TS"]
    today_day = ts.todaydate().day
    today_month = ts.todaydate().month
    today_year = ts.todaydate().year

    try:
        veranst_id = None
        veranst_timestamp = None
        for pkey, parm in result:
            if pkey == "berater":
                berater.extend(parm)
            elif pkey == "besucher":
                for besId, besParm in parm:
                    besucher.update({besId : dict(besParm)})
            else:
                if pkey == "veranst-datum":
                    veranst_datum = parm
                elif pkey == "veranst-zeit-von":
                    veranst_zeit_von = parm
                elif pkey == "veranst-zeit-bis":
                    veranst_zeit_bis = parm
                elif pkey == "veranst-zeit-dauer":
                    veranst_zeit_dauer = parm
                elif pkey == "veranst-typ":
                    veranst_typ = parm
                elif pkey == "veranst-ort":
                    veranst_ort = parm
                elif pkey == "veranst-thema":
                    veranst_thema = parm
                elif pkey == "main-id":
                    veranst_id = parm
                elif pkey == "item-timestamp":
                    veranst_timestamp = parm
                elif pkey == "besucher-remove":
                    besucher_remove = parm
        try:
            db = get_db()
            if not db:
                raise mariadb.PoolError()
            db.begin()
            cur = db.cursor(dictionary=True)

            cur.execute("SELECT id,bezeichnung FROM tVeranstTyp WHERE id=?", (veranst_typ,))
            veranst_bez = cur.fetchone()["bezeichnung"]
            bezeichnung = f"{veranst_bez}, {parser.parse(veranst_datum).strftime('%d.%m.%Y')}, {veranst_zeit_von} bis {veranst_zeit_bis}"

            update_allowed = True
            if veranst_id is not None:
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tVeranst WHERE id=? FOR UPDATE", (veranst_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == veranst_timestamp:
                    cur.execute("update tVeranst set sperre=null,typ=?,ort=?,thema=NULLIF(?,-1),datum=?,von=?,bis=?,dauer=?,bezeichnung=? where id=?", (veranst_typ, veranst_ort, veranst_thema, veranst_datum, veranst_zeit_von, veranst_zeit_bis, veranst_zeit_dauer, bezeichnung, veranst_id))
                    cur.execute("delete from tBeraterVer where VeranstID=?", (veranst_id,))
                    last_id = veranst_id
                    rc_code["id"] = veranst_id
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                    rc_code["id"] = veranst_id
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
                    rc_code["id"] = veranst_id
            else:
                cur.execute("insert into tVeranst(typ,ort,thema,datum,von,bis,dauer,bezeichnung) values(?,?,NULLIF(?,-1),?,?,?,?,?)", (veranst_typ, veranst_ort, veranst_thema, veranst_datum, veranst_zeit_von, veranst_zeit_bis, veranst_zeit_dauer, bezeichnung))
                last_id = cur.lastrowid
                rc_code["id"] = last_id

            if update_allowed:
                for berId in berater:
                    cur.execute("insert into tBeraterVer(BeraterID,VeranstID) values(?,?)", (berId, last_id))
                for besId, besParm in besucher.items():
                    if "id" in besParm:
                        if besParm["wl-prev"] != besParm["wl"]:
                            cur.execute(f"insert into tBesucheLOG(Action,BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL) \
                                        select 'change-wl-by-event',BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL from tBesuche where id=?", (besParm["id"],))
                        cur.execute("UPDATE tBesuche set BesucherID=?,VeranstID=?,ThemenID=NULLIF(?,-1),GeraeteID=NULLIF(?,-1),Spende=?,BesucherWL=? WHERE id=?", (besId, last_id, besParm["thema"], besParm["geraet"], besParm["spende"], besParm["wl"], besParm["id"]))
                        current_app.logger.debug("Ersetzt in tBesuche: RowCount=%s, Warnings=%s, ID=%s, Bes.ID=%s, VeranstID=%s", cur.rowcount, cur.warnings, besParm["id"], besId, last_id)
                    else:
                        cur.execute("insert into tBesuche(BesucherID,VeranstID,ThemenID,GeraeteID,Spende,BesucherWL,TagInt,Monat,Jahr) values(?,?,NULLIF(?,-1),NULLIF(?,-1),?,?,?,?,?)", (besId, last_id, besParm["thema"], besParm["geraet"], besParm["spende"], besParm["wl"], today_day, today_month, today_year))
                        row_id = cur.lastrowid
                        current_app.logger.debug("Eingefügt in tBesuche: RowCount=%s, Warnings=%s, Bes.ID=%s, VeranstID=%s, ID=%s", cur.rowcount, cur.warnings, besId, last_id, row_id)
                        cur.execute(f"insert into tBesucheLOG(BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL) \
                                    select BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL from tBesuche where id=?", (row_id,))
                for itemId in besucher_remove:
                    cur.execute(f"insert into tBesucheLOG(Action,BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL) \
                                select 'delete-by-event',BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL from tBesuche where id=?", (itemId,))
                    cur.execute("DELETE from tBesuche where id=?", (itemId,))
                    current_app.logger.debug("Entfernt aus tBesuche: RowCount=%s, Warnings=%s, ID=%s, VeranstID=%s", cur.rowcount, cur.warnings, itemId, last_id)

                if veranst_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Bezeichnung=%s", veranst_id, bezeichnung)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Bezeichnung=%s", last_id, bezeichnung)
                    rc_code["mode"] = "INS"
            db.commit()
            cur.close()
            db.close()
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-veranst/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-events-release/", methods=['POST'])
def ax_submit_veranst_release():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    try:
        veranst_id = None
        veranst_timestamp = None
        for pkey, parm in result:
            if pkey == "item-id":
                veranst_id = parm
            elif pkey == "item-timestamp":
                veranst_timestamp = parm
        try:
            db = get_db()
            if not db:
                raise mariadb.PoolError()
            db.begin()
            cur = db.cursor(dictionary=True)

            if veranst_id is not None:
                rc_code["id"] = veranst_id
                cur.execute("SELECT IFNULL(sperre,'IGNORE') as sperre FROM tVeranst WHERE id=? FOR UPDATE", (veranst_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == veranst_timestamp:
                    cur.execute("update tVeranst set sperre=null where id=? and sperre=?", (veranst_id, veranst_timestamp))
                    current_app.logger.debug("RELEASE: Timestamp entfernt. Id=%s, Timestamp=%s, RowCount=%s, Warnings=%s", veranst_id, veranst_timestamp, cur.rowcount, cur.warnings)
                else:
                    rc_code["status"] = "IGNORE"
            db.commit()
            cur.close()
            db.close()
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-veranst-release/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
