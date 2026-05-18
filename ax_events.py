import mariadb, sys
from icalendar.prop import vDDDTypes, vText
from caldav import davclient
from flask import Blueprint
from flask import current_app
from flask import request, session
from flask import render_template
from dateutil import parser

from .ax_default import mx_get_overview, mx_submit_release, mx_get_edit
from .db import get_db
from . import credentials

bp = Blueprint("ax_events", __name__)

@bp.route("/ax-get-events-edit/", methods=['POST'])
def ax_get_veranst_edit():
    queries={}
    queries['berater'] = {'sql':"SELECT id,BeraterID FROM tBeraterVer WHERE VeranstID=?"}
    queries['besucher'] = {'sql':"SELECT id,BesucherID,REPLACE(FORMAT(spende,2,'de_DE'),'.','') as spende,IF(BesucherWL=true,true,false) as BesucherWL \
                    FROM tBesuche WHERE VeranstID=?"}
    select_field = "typ,REPLACE(FORMAT(spenden,2,'de_DE'),'.','') as spenden,IFNULL(ort,-1) as ort,DATE_FORMAT(DATE(datum),'%Y-%m-%d') as datum,von,bis,dauer,IFNULL(thema,-1) as thema,IFNULL(cal_uid,'') as cal_uid"
    return mx_get_edit(request, current_app, table_name="tVeranst", data_key="veranst", queries=queries, select_field=select_field)


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
    except mariadb.PoolError as err:
        current_app.logger.error("Pool-Fehler: ax-check-veranstort= %s", err)
        rc_code["status"] = "ERR"
    except mariadb.Error as err:
        current_app.logger.error("Datenbank-Fehler: ax-check-veranstort= %s", err)
        rc_code["status"] = "ERR"
        db.close()
    
    return rc_code


@bp.route("/ax-get-events-overview/", methods=['POST'])
def ax_get_events_overview():
    rc_code = mx_get_overview(request, current_app, html_template_body="index_body.html", 
                              sql=["SELECT a.id,DATE_FORMAT(DATE(a.datum),'%d.%m.%Y') as datum,a.bezeichnung,IFNULL(d.MaxBesucher,'--') as plaetze,IFNULL(b.anzahl,'--') as anzahl_s,IFNULL(c.anzahl,'--') as anzahl_b from tVeranst a \
                    left join (select count(BesucherID) as anzahl,VeranstID from tBesuche group by VeranstID) b ON (b.VeranstID=a.id) \
                    left join (select count(BeraterID) as anzahl,VeranstID from tBeraterVer group by VeranstID) c on (c.VeranstID=a.id) \
                    left join tOrte d on (a.Ort=d.id)", 
                    "ORDER BY a.datum desc, a.id desc"], search_field=["a.datum"])

    return rc_code


@bp.route("/ax-submit-events/", methods=['POST'])
def ax_submit_veranst():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    changeUser = session['coach_name']
    berater = {}
    besucher = {}
    ts = current_app.config["TS"]
    add_calevent = bool(current_app.config["add-new-calevent"] == '1')

    try:
        veranst_id = None
        veranst_timestamp = None
        for pkey, parm in result:
            if pkey == "berater":
                for besId, besParm in parm:
                    berater.update({besId : besParm})
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
                elif pkey == "veranst-spende":
                    veranst_spende = float(parm.replace(",", '.'))
                elif pkey == "veranst-ort":
                    veranst_ort = parm
                elif pkey == "veranst-cal_uid":
                    veranst_cal_uid = parm
                elif pkey == "veranst-thema":
                    veranst_thema = parm
                elif pkey == "main-id":
                    veranst_id = parm
                elif pkey == "item-timestamp":
                    veranst_timestamp = parm
                elif pkey == "besucher-remove":
                    besucher_remove = parm
                elif pkey == "berater-remove":
                    berater_remove = parm
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
            insert_done = False
            if veranst_id is not None:
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tVeranst WHERE id=? FOR UPDATE", (veranst_id,))
                timestamp = str(cur.fetchone()["sperre"])
                if timestamp == veranst_timestamp:
                    cur.execute("update tVeranst set sperre=null,typ=?,ort=NULLIF(?,-1),spenden=?,thema=NULLIF(?,-1),datum=?,von=?,bis=?,dauer=?,bezeichnung=?, AnlageUser=?,AnlageDatum=current_timestamp() where id=?", 
                                (veranst_typ, veranst_ort, veranst_spende, veranst_thema, veranst_datum, veranst_zeit_von, veranst_zeit_bis, veranst_zeit_dauer, bezeichnung, changeUser, veranst_id))
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
                cur.execute("insert into tVeranst(typ,ort,spenden,thema,datum,von,bis,dauer,bezeichnung,AnlageUser) values(?,NULLIF(?,-1),?,NULLIF(?,-1),?,?,?,?,?,?)", 
                            (veranst_typ, veranst_ort, veranst_spende, veranst_thema, veranst_datum, veranst_zeit_von, veranst_zeit_bis, veranst_zeit_dauer, bezeichnung, changeUser))
                last_id = cur.lastrowid
                rc_code["id"] = last_id
                insert_done = True

            if update_allowed:
                for itemId in berater_remove:
                    cur.execute("delete from tBeraterVer where id=?", (itemId,))
                    current_app.logger.debug("Entfernt in tBeraterVer: RowCount=%s, Warnings=%s, ID=%s, VeranstID=%s", cur.rowcount, cur.warnings, itemId, last_id)
                cur.execute("select Thema from tThemen where id=?", (veranst_thema,))
                verThema = cur.fetchone()
                Thema = ''
                if cur.rowcount > 0:
                    Thema = verThema['Thema']
                for berId, verId in berater.items():
                    cur.execute("select Nachname,Vorname from tBerater where id=?", (berId,))
                    berName = cur.fetchone()
                    Nachname = Vorname = ''
                    if cur.rowcount > 0:
                        Nachname = berName['Nachname']
                        Vorname = berName['Vorname']
                    if verId != '-1':
                        cur.execute("update tBeraterVer set BeraterID=?,VeranstID=?,AnlageUser=?,AnlageDatum=current_timestamp(),Nachname=NULLIF(?,''),Vorname=NULLIF(?,''),VeranstThema=NULLIF(?,''),VeranstBez=NULLIF(?,'') where id=?", 
                                    (berId, last_id, changeUser, Nachname, Vorname, Thema, bezeichnung, verId))
                        current_app.logger.debug("Ersetzt in tBeraterVer: RowCount=%s, Warnings=%s, ID=%s, Ber.ID=%s, VeranstID=%s", cur.rowcount, cur.warnings, verId, berId, last_id)
                    else:
                        cur.execute("insert into tBeraterVer(BeraterID,VeranstID,AnlageUser,Nachname,Vorname,VeranstThema,VeranstBez) values(?,?,?,NULLIF(?,''),NULLIF(?,''),NULLIF(?,''),NULLIF(?,''))", 
                                    (berId, last_id, changeUser, Nachname, Vorname, Thema, bezeichnung))
                        ins_id = cur.lastrowid
                        current_app.logger.debug("Eingefügt in tBeraterVer: RowCount=%s, Warnings=%s, ID=%s, Ber.ID=%s, VeranstID=%s", cur.rowcount, cur.warnings, ins_id, berId, last_id)
                for besId, besParm in besucher.items():
                    # spende = float(besParm["spende"].replace(",", '.'))
                    spende = 0.00
                    cur.execute("select Nachname,Vorname from tBesucher where id=?", (besId,))
                    besName = cur.fetchone()
                    Nachname = Vorname = ''
                    if cur.rowcount > 0:
                        Nachname = besName['Nachname']
                        Vorname = besName['Vorname']
                    if "id" in besParm:
                        if besParm["wl-prev"] != besParm["wl"]:
                            cur.execute(f"insert into tBesucheLOG(Action,BesucherID,VeranstID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL) \
                                        select 'change-wl-by-event',BesucherID,VeranstID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL from tBesuche where id=?", (besParm["id"],))
                        cur.execute("UPDATE tBesuche set BesucherID=?,VeranstID=?,Spende=?,BesucherWL=?,AnlageUser=?,AnlageDatum=current_timestamp(),Nachname=NULLIF(?,''),Vorname=NULLIF(?,''),VeranstThema=NULLIF(?,''),VeranstBez=NULLIF(?,'') WHERE id=?", 
                                    (besId, last_id, spende, besParm["wl"], changeUser, Nachname, Vorname, Thema, bezeichnung, besParm["id"]))
                        current_app.logger.debug("Ersetzt in tBesuche: RowCount=%s, Warnings=%s, ID=%s, Bes.ID=%s, VeranstID=%s", cur.rowcount, cur.warnings, besParm["id"], besId, last_id)
                        cur.execute("UPDATE tBesucher set LetztDatum=? WHERE id=? && (LetztDatum<? || LetztDatum is null)", (veranst_datum, besId, veranst_datum))
                        current_app.logger.debug("Letztes Veranst-Datum in tBesucher: RowCount=%s, Warnings=%s, Bes.ID=%s, VeranstDat=%s", cur.rowcount, cur.warnings, besId, veranst_datum)
                    else:
                        cur.execute("insert into tBesuche(BesucherID,VeranstID,Spende,BesucherWL,AnlageUser,Nachname,Vorname,VeranstThema,VeranstBez) values(?,?,?,?,?,NULLIF(?,''),NULLIF(?,''),NULLIF(?,''),NULLIF(?,''))", 
                                    (besId, last_id, spende, besParm["wl"], changeUser, Nachname, Vorname, Thema, bezeichnung))
                        row_id = cur.lastrowid
                        current_app.logger.debug("Eingefügt in tBesuche: RowCount=%s, Warnings=%s, Bes.ID=%s, VeranstID=%s, ID=%s", cur.rowcount, cur.warnings, besId, last_id, row_id)
                        cur.execute(f"insert into tBesucheLOG(BesucherID,VeranstID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL) \
                                    select BesucherID,VeranstID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL from tBesuche where id=?", (row_id,))
                        cur.execute("UPDATE tBesucher set LetztDatum=? WHERE id=? && (LetztDatum<? || LetztDatum is null)", (veranst_datum, besId, veranst_datum))
                        current_app.logger.debug("Letztes Veranst-Datum in tBesucher: RowCount=%s, Warnings=%s, Bes.ID=%s, VeranstDat=%s", cur.rowcount, cur.warnings, besId, veranst_datum)
                for itemId in besucher_remove:
                    cur.execute(f"insert into tBesucheLOG(Action,BesucherID,VeranstID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL) \
                                select 'delete-by-event',BesucherID,VeranstID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL from tBesuche where id=?", (itemId,))
                    cur.execute("SELECT BesucherID from tBesuche where id=?", (itemId,))
                    row = cur.fetchone()
                    besId = row['BesucherID']
                    current_app.logger.debug("Vor Entfernen holen BesucherID aus tBesuche: RowCount=%s, Warnings=%s, ID=%s, BesucherID=%s", cur.rowcount, cur.warnings, itemId, besId)
                    cur.execute("DELETE from tBesuche where id=?", (itemId,))
                    current_app.logger.debug("Entfernt aus tBesuche: RowCount=%s, Warnings=%s, ID=%s, VeranstID=%s", cur.rowcount, cur.warnings, itemId, last_id)
                    cur.execute("select max(b.Datum) as maxdatum from tBesuche a join tVeranst b on a.VeranstID=b.id where a.BesucherID=?", (besId,))
                    row = cur.fetchone()
                    letztDat = row['maxdatum']
                    current_app.logger.debug("Letztes Datum Besuch aus tBesuche: RowCount=%s, Warnings=%s, BesucherID=%s, Datum=%s", cur.rowcount, cur.warnings, besId, letztDat)
                    cur.execute("UPDATE tBesucher set LetztDatum=? WHERE id=?", (letztDat, besId))
                    current_app.logger.debug("Letztes Veranst-Datum in tBesucher: RowCount=%s, Warnings=%s, Bes.ID=%s, VeranstDat=%s", cur.rowcount, cur.warnings, besId, letztDat)

                if veranst_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Bezeichnung=%s", veranst_id, bezeichnung)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Bezeichnung=%s", last_id, bezeichnung)
                    rc_code["mode"] = "INS"
            
            if add_calevent:
                try:
                    # Verbindung herstellen
                    if not current_app.config['TEST_RUN']: 
                        # Production
                        url = credentials.Passwords.NC_URL
                        username = credentials.Passwords.NC_USER
                        password = credentials.Passwords.NC_PWD
                    else: 
                        # Development
                        url = credentials.Passwords.NC_URL_DEV
                        username = credentials.Passwords.NC_USER_DEV
                        password = credentials.Passwords.NC_PWD_DEV
                    client = davclient.DAVClient(url, username=username, password=password)
                    # Benutzer auswählen
                    principal = client.get_principal()
                    calendars = principal.get_calendars()
                    # Den 2.Kalender=Terminplanung auswählen
                    calendar = calendars[1]
                    current_app.logger.info("Kalender '%s' von '%s' gefunden.", calendar.get_display_name(), principal.get_display_name())
                    # Termin-Daten erstellen
                    (datfrom, datto, tzid) = ts.convert(veranst_datum, veranst_zeit_von, veranst_zeit_bis)
                    if veranst_ort == '-1':
                        veranst_ort_text = "Noch nicht ausgewählt."
                    else:
                        cur.execute("SELECT Bezeichnung from tOrte where id=?", (veranst_ort,))
                        row = cur.fetchone()
                        if cur.rowcount > 0:
                            veranst_ort_text = row['Bezeichnung']
                        else:
                            veranst_ort_text = "Veranstaltungsort nicht gefunden."
                    # Termin zum Kalender hinzufügen
                    if insert_done:
                        cal_event = calendar.add_event(dtstart=datfrom, dtend=datto, summary=bezeichnung, description=f"Von Besucherverwaltung automatisch angelegt, ID={last_id}", location=veranst_ort_text, categories="Bildung")
                        print(cal_event.get_data())
                        # ID des Events zur Veranstaltung hinzufügen
                        cur.execute("update tVeranst set cal_uid=? where id=?", (cal_event.id, last_id))
                        current_app.logger.info("Cal_Event_Id in tVeranst eingefügt: RowCount=%s, Warnings=%s, VeranstID=%s, Cal-ID=%s", cur.rowcount, cur.warnings, last_id, cal_event.id)
                        current_app.logger.info("Termin erfolgreich in %s von %s erstellt: %s %s %s %s", calendar.get_display_name(), principal.get_display_name(), bezeichnung, veranst_datum, veranst_zeit_von, veranst_zeit_bis)
                    elif veranst_cal_uid != '':
                        # ID des Events zur Veranstaltung aktualisieren
                        cal_event = calendar.get_event_by_uid(veranst_cal_uid)
                        print(cal_event.get_data(), cal_event.component)
                        cal_event.component['DTSTART'] = vDDDTypes(datfrom, params={'TZID':tzid})
                        cal_event.component['DTEND'] = vDDDTypes(datto, params={'TZID':tzid})
                        cal_event.component['SUMMARY'] = vText(bezeichnung)
                        cal_event.component['LOCATION'] = vText(veranst_ort_text)
                        cal_event.component['LAST-MODIFIED'] = vDDDTypes(ts.todaytime_utc())
                        cal_event.save()
                        print(cal_event.get_data(), cal_event.component)
                        current_app.logger.info("Termin erfolgreich in %s von %s geändert: %s %s %s %s", calendar.get_display_name(), principal.get_display_name(), bezeichnung, veranst_datum, veranst_zeit_von, veranst_zeit_bis)
                    else:
                        current_app.logger.info("Termin nicht in %s von %s gefunden: %s %s %s %s", calendar.get_display_name(), principal.get_display_name(), bezeichnung, veranst_datum, veranst_zeit_von, veranst_zeit_bis)
                    client.close()
                except:
                    (type, value, traceback) = sys.exc_info()
                    current_app.logger.critical("Calendar-Event-Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
                    rc_code["status"] = "ERR"
                    db.rollback()
                    db.close()
                    current_app.logger.error("Calendar-Event-Datenbank-Rollback")

            db.commit()
            cur.close()
            db.close()
        except mariadb.PoolError as err:
            current_app.logger.error("Pool-Fehler: %s/ax-submit-veranst/%s", bp.name, err)
            rc_code["status"] = "ERR"
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
    rc_code = mx_submit_release(request, current_app, table_name="tVeranst")
    return rc_code
