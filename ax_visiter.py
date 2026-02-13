import mariadb
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request
from datetime import date
import sys

from .db import get_db
from . import version
from . import tools

bp = Blueprint("ax_visitor", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.route("/ax-fd-visiter/<pattern>")
def ax_fd_visiter(pattern):
    dbdata={}
    try:
        dbdata.update({"status":"OK"})
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        search_like = "%" + pattern + "%"
        cur.execute("SELECT id,vorname,nachname,IFNULL(email,'--') as email,IF(telefon='','--',Telefon) as telefon FROM tBesucher WHERE (vorname like ? or nachname like ?) ORDER BY nachname,vorname", (search_like, search_like))
        dbdata.update({"visiter":cur.fetchall()})
        cur.close()
        db.close()
        anzahl_fetched = len(dbdata["visiter"])
        current_app.logger.info("Suchen Besucher mit Pattern: %s, Anzahl gelesen=%s", pattern, anzahl_fetched)
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-fd-visiter/%s/%s", bp.name, pattern, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-get-visiter/<pattern>")
def ax_get_visiter(pattern):
    dbdata={}
    try:
        dbdata.update({"status":"OK"})
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        cur.execute(f"SELECT id,vorname,nachname,IFNULL(email,'--') as email,IF(telefon='','--',Telefon) as telefon FROM tBesucher WHERE id in({pattern})")
        pattern_list = pattern.split(",")
        dbdata.update({"visiter":[None] * len(pattern_list)})
        seq = 1
        while seq <= cur.rowcount:
            db_row = cur.next()
            pos = pattern_list.index(str(db_row["id"]))
            dbdata["visiter"][pos] = db_row
            seq += 1

        cur.close()
        db.close()
        current_app.logger.info("Einlesen Besucher mit Pattern: %s, Anzahl gelesen=%s", pattern, seq - 1)
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-visiter/%s/%s", bp.name, pattern, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-submit-quick-visiter/", methods=['POST'])
def ax_submit_quick_visiter():
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    result = request.get_json()
    result_map = dict(result)
    today=date.today()
    newsletter = True
    if result_map["email"] is None:
        newsletter = False

    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        db.begin()
        cur = db.cursor(dictionary=True)

        cur.execute("select MAX(KundenNr)+1 as KundenNr from tBesucher")
        max_kdnr = cur.fetchone()["KundenNr"]

        cur.execute("insert into tBesucher(KundenNr,Vorname,Nachname,Telefon,EMail,Aktiv,Newsletter,AufnDatum) \
                    values(?,?,?,?,NULLIF(?,''),?,?,?)", (max_kdnr, result_map["vorname"], result_map["nachname"], result_map["telefon"], result_map["email"], True, newsletter, today))
        last_id = cur.lastrowid
        rc_code["last_id"] = last_id
        rc_code.update(result_map)
        db.commit()
        cur.close()
        db.close()
        current_app.logger.info("Quick-Insert: Besucher hinzugefügt, ID=%s, Vorname=%s, Nachname=%s, Telefon=%s, E-Mail=%s", last_id, result_map["vorname"], result_map["nachname"], result_map["telefon"], result_map["email"])
    except mariadb.Error as err:
        current_app.logger.error("Datenbankfehler: ax-submit-quick-visiter= %s", err)
        rc_code["status"] = "ERR"
        db.rollback()
        db.close()
        current_app.logger.error("Datenbank-Rollback")
    
    return rc_code


@bp.route("/ax-get-visiter-edit/", methods=['POST'])
def ax_get_visiter_edit():
    result = request.get_json()
    result_map = dict(result)
    visiter_id = result_map["main-id"]
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
            if timestamp_P is not None and item_id_head != visiter_id:
                """ Vorherige Besucher-ID entsperren """
                cur.execute("update tBesucher set sperre=null where id=? and sperre IS NOT NULL and sperre=?", (item_id_head, timestamp_P))
                current_app.logger.debug("Vorherige Sperre=%s für Besucher=%s aufgehoben.", timestamp_P, item_id_head)
            
        cur.execute("UPDATE tBesucher SET Sperre=? WHERE Sperre IS NULL AND id=?", (timestamp_N, visiter_id))
        db.commit()
        cur.execute("SELECT id,KundenNr,sperre,Nachname,Vorname,IFNULL(Anrede,-1) as Anrede,IFNULL(Strasse,'') as Strasse,IFNULL(Ort,'') as Ort,IFNULL(PLZ,'') as PLZ,IFNULL(EMail,'') as EMail,Telefon,\
                    IF(Aktiv=TRUE,TRUE,FALSE) as Aktiv,IF(Newsletter=TRUE,TRUE,FALSE) as Newsletter,IFNULL(Bemerkung,'') as Bemerkung,DATE_FORMAT(DATE(AufnDatum),'%Y-%m-%d') as datum \
                    FROM tBesucher WHERE id=?", (visiter_id,))
        dbdata.update({"visiter":cur.fetchone()})

        act_timestamp = str(dbdata["visiter"]["sperre"])
        if act_timestamp == timestamp_N:
            dbdata.update({"timestamp":timestamp_N})
            current_app.logger.debug("Neue Sperre=%s für Besucher=%s eingerichtet.", timestamp_N, visiter_id)
        elif timestamp_P is not None and act_timestamp == timestamp_P:
            dbdata.update({"timestamp":timestamp_P})
        else:
            dbdata.update({"status":"LCK"})

        cur.execute("SELECT distinct a.id,a.VeranstID,b.Bezeichnung,IFNULL(c.Bezeichnung,'--') as ort,DATE_FORMAT(DATE(b.Datum),'%d.%m.%Y') as datum, \
                    IF(a.BesucherWL=true,true,false) as WL \
                    FROM tBesuche a \
                    JOIN tVeranst b ON a.VeranstID=b.id \
                    LEFT JOIN tOrte c ON b.Ort=c.id \
                    WHERE a.BesucherID=? ORDER BY b.id DESC", (visiter_id,))
        dbdata.update({"events":cur.fetchall()})
        
        cur.close()
        db.close()
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: %s/ax-get-visiter-edit/%s/%s", bp.name, visiter_id, err)
        dbdata.update({"status":"ERR"})

    return dbdata


@bp.route("/ax-submit-visiter-release/", methods=['POST'])
def ax_submit_visiter_release():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    try:
        besucher_id = None
        besucher_timestamp = None
        for pkey, parm in result:
            if pkey == "item-id":
                besucher_id = parm
            elif pkey == "item-timestamp":
                besucher_timestamp = parm
        try:
            db = get_db()
            if not db:
                raise mariadb.PoolError()
            db.begin()
            cur = db.cursor(dictionary=True)

            if besucher_id is not None:
                rc_code["id"] = besucher_id
                cur.execute("SELECT IFNULL(sperre,'IGNORE') as sperre FROM tBesucher WHERE id=? FOR UPDATE", (besucher_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == besucher_timestamp:
                    cur.execute("update tBesucher set sperre=null where id=? and sperre=?", (besucher_id, besucher_timestamp))
                    current_app.logger.debug("RELEASE: Timestamp entfernt. Id=%s, Timestamp=%s, RowCount=%s, Warnings=%s", besucher_id, besucher_timestamp, cur.rowcount, cur.warnings)
                else:
                    rc_code["status"] = "IGNORE"
            db.commit()
            cur.close()
            db.close()
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-besucher-release/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-get-visiter-overview/", methods=['POST'])
def ax_get_visiter_overview():
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
            sql_parms = f"WHERE KundenNr={overview_search}"
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

        cur.execute(f"SELECT a.id,a.KundenNr,a.Vorname,a.Nachname,IF(a.Telefon='','--',Telefon) as Telefon,IFNULL(a.EMail,'--') as EMail, \
                    DATE_FORMAT(DATE(a.AufnDatum),'%d.%m.%Y') as datum,IFNULL(b.anzahl,'--') as Anzahl \
                    from tBesucher a \
                    left join (select g.BesucherID,count(*) as anzahl from (select VeranstID,BesucherID from tBesuche group by BesucherID,VeranstID) g group by g.BesucherID) b ON a.id=b.BesucherID \
                    {sql_parms} \
                    ORDER BY a.AufnDatum DESC LIMIT {overview_offset}, {overview_readlines}")
        dbdata.update({"visiters":cur.fetchall()})
        len_vis = len(dbdata["visiters"])
        show_lines = len_vis
        if len_vis > overview_maxlines:
            show_lines = overview_maxlines
            is_more_lines = True
            
        rc_code["html"] = render_template("verwBesucher_body.html", visiters=dbdata["visiters"][0:show_lines])
        rc_code["pagination"] = is_more_lines
        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        rc_code["status"] = "ERR"

    return rc_code


@bp.route("/ax-submit-visiter/", methods=['POST'])
def ax_submit_visiter():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "id":"(Neu)", "kdnr":"(Neu)", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}

    try:
        item_id = None
        item_timestamp = None
        veranst_remove = None
        for pkey, parm in result:
            if pkey == "datum":
                besucher_datum = parm
            elif pkey == "anrede":
                besucher_anrede = parm
            elif pkey == "vorname":
                besucher_vorname = parm
            elif pkey == "nachname":
                besucher_nachname = parm
            elif pkey == "strasse":
                besucher_strasse = parm
            elif pkey == "plz":
                besucher_plz = parm
            elif pkey == "ort":
                besucher_ort = parm
            elif pkey == "email":
                besucher_email = parm
            elif pkey == "telefon":
                besucher_telefon = parm
            elif pkey == "bemerkung":
                besucher_bemerkung = parm
            elif pkey == "newsl":
                besucher_newsl = parm
            elif pkey == "aktiv":
                besucher_aktiv = parm
            elif pkey == "main-id":
                item_id = parm
            elif pkey == "item-timestamp":
                item_timestamp = parm
            elif pkey == "veranst-remove":
                veranst_remove = parm
        
        print(veranst_remove)
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
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre,KundenNr FROM tBesucher WHERE id=? FOR UPDATE", (item_id,))
                row_data = cur.fetchone()
                timestamp = str(row_data["sperre"])
                rc_code["kdnr"] = str(row_data["KundenNr"])
                if timestamp == item_timestamp:
                    cur.execute("update tBesucher set sperre=null,Nachname=?,Vorname=?,Anrede=NULLIF(?,-1),Strasse=NULLIF(?,''),Ort=NULLIF(?,''),PLZ=NULLIF(?,''),EMail=NULLIF(?,''),Telefon=?,Aktiv=?,Newsletter=?,Bemerkung=NULLIF(?,''),AufnDatum=? where id=?", 
                                (besucher_nachname, besucher_vorname, besucher_anrede, besucher_strasse, besucher_ort, besucher_plz, besucher_email, besucher_telefon, besucher_aktiv, besucher_newsl, besucher_bemerkung, besucher_datum, item_id))
                    if len(veranst_remove) > 0:
                        remove_verId = []
                        remove_rowId = []
                        for verId, rowId in veranst_remove:
                            remove_verId.append(verId)
                            remove_rowId.append(rowId)
                        veranst_search = ",".join(remove_rowId)
                        cur.execute(f"insert into tBesucheLOG(Action,BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL) \
                                    select 'delete-by-visiter',BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL from tBesuche where id in ({veranst_search})")
                        cur.execute(f"delete from tBesuche where id in ({veranst_search})")
                        current_app.logger.debug("Entfernt Id=%s aus tBesuche für Besucher=%s: RowCount=%s, Warnings=%s", veranst_search, item_id, cur.rowcount, cur.warnings)
                        rc_code["result_WL"] = tools.setVisiterWL(cur, remove_verId)
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
            else:
                cur.execute("select GET_LOCK('tBesucher',20) as get_lock")
                is_locked = cur.fetchone()
                if is_locked["get_lock"] == 0:
                    current_app.logger.error("Für Datensatz: Name=%s %s, konnte kein GET_LOCK ausgeführt werden.", besucher_vorname, besucher_nachname)
                    raise mariadb.OperationalError("Kein Lock für tBesucher möglich.")
                cur.execute("select MAX(KundenNr)+1 as KundenNr from tBesucher")
                max_kdnr = cur.fetchone()["KundenNr"]
                cur.execute("select RELEASE_LOCK('tBesucher') as unlocked")
                is_unlocked = cur.fetchone()
                if is_unlocked["unlocked"] == 0:
                    current_app.logger.error("Für Datensatz: ID=%s, Name=%s %s, Kd-Nr=%s, konnte kein RELEASE_LOCK ausgeführt werden.", last_id, besucher_vorname, besucher_nachname, max_kdnr)
                cur.execute("insert into tBesucher(KundenNr,Nachname,Vorname,Anrede,Strasse,Ort,PLZ,EMail,Telefon,Aktiv,Newsletter,Bemerkung,AufnDatum) \
                            values(?,?,?,?,NULLIF(?,''),NULLIF(?,''),NULLIF(?,''),NULLIF(?,''),?,?,?,NULLIF(?,''),?)", 
                            (max_kdnr, besucher_nachname, besucher_vorname, besucher_anrede, besucher_strasse, besucher_ort, besucher_plz, besucher_email, besucher_telefon, besucher_aktiv, besucher_newsl, besucher_bemerkung, besucher_datum))
                last_id = cur.lastrowid
                rc_code["id"] = last_id
                rc_code["kdnr"] = max_kdnr

            if update_allowed:
                if item_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Name=%s %s", last_id, besucher_vorname, besucher_nachname)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Name=%s %s, Kd-Nr=%s", last_id, besucher_vorname, besucher_nachname, max_kdnr)
                    rc_code["mode"] = "INS"
            db.commit()
            cur.close()
            db.close()
        except mariadb.IntegrityError as err:
            rc_code["status"] = "DBL"
            current_app.logger.warning("Datenbank-doppelter Eintrag: %s/ax-submit-besucher/%s", bp.name, err)
            db.rollback()
            db.close()
            current_app.logger.warning("Datenbank-Rollback-doppelter Eintrag")
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-besucher/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
