import mariadb, subprocess
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request, make_response
from werkzeug.exceptions import abort

from .db import get_db, credentials

bp = Blueprint("ax_queries", __name__)

@bp.route("/ax-qy-visiter/<store>", methods=['GET'])
def ax_qy_visiter(store):
    sql_file = "qy_visiter.sql"
    if store == 'store-yes':
        rc_code = db_collect(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = "Jahr;Monat;Anzahl Besucher;Summe Spenden\n"
        for row in rc_code['result_list']:
            (year, month, vis, spen) = row
            output += f"{year};{month};{vis};{spen}\n"
    else:
        rc_code = mariadb_client(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = rc_code['result_list']
    return send_response(output, store, "Besucher_Gesamt_im_Monat.csv")


@bp.route("/ax-qy-visiter-info/<store>", methods=['GET'])
def ax_qy_visiter_info(store):
    sql_file = "qy_visiter_info.sql"
    if store == 'store-yes':
        rc_code = db_collect(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = "Anzahl Besucher;Thema\n"
        for row in rc_code['result_list']:
            (vis, thema) = row
            output += f"{vis};{thema}\n"
    else:
        rc_code = mariadb_client(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = rc_code['result_list']
    return send_response(output, store, "Besucher_Infothemen.csv")


@bp.route("/ax-qy-visiter-ext/<store>", methods=['GET'])
def ax_qy_visiter_ext(store):
    sql_file = "qy_visiter_ext.sql"
    if store == 'store-yes':
        rc_code = db_collect(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = "Ort;Jahr;Monat;Anzahl Besucher\n"
        for row in rc_code['result_list']:
            (ort, year, month, vis) = row
            output += f"{ort};{year};{month};{vis}\n"
    else:
        rc_code = mariadb_client(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = rc_code['result_list']
    return send_response(output, store, "Besucher_Extern.csv")


@bp.route("/ax-qy-visiter-events/<store>", methods=['GET'])
def ax_qy_visiter_events(store):
    sql_file = "qy_visiter_events.sql"
    if store == 'store-yes':
        rc_code = db_collect(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = "Nr;Bezeichnung;Jahr;Monat;Tag;Von;Bis;Dauer;Spenden;Nachname;Vorname;Newsletter;AufnDatum;LetzterBesuch;Telefon;EMail;Aktiv\n"
        for row in rc_code['result_list']:
            (id, text, year, month, day, f, t, d, amount, n, v, nl, ad, ld, tl, e, a) = row
            output += f"{id};{text};{year};{month};{day};{f};{t};{d};{amount};{n};{v};{nl};{ad};{ld};{tl};{e};{a}\n"
    else:
        rc_code = mariadb_client(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = rc_code['result_list']
    return send_response(output, store, "Veranstaltung_Besucher.csv")


@bp.route("/ax-qy-coaches-events/<store>", methods=['GET'])
def ax_qy_coaches_events(store):
    sql_file = "qy_coaches_events.sql"
    if store == 'store-yes':
        rc_code = db_collect(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = "Nr;Bezeichnung;Jahr;Monat;Tag;Von;Bis;Dauer;Spenden;Vorname;Nachname;Telefon;Mobil;EMail;Aktiv\n"
        for row in rc_code['result_list']:
            (id, text, year, month, day, f, t, d, amount, v, n, tl, mob, e, a) = row
            output += f"{id};{text};{year};{month};{day};{f};{t};{d};{amount};{v};{n};{tl};{mob};{e};{a}\n"
    else:
        rc_code = mariadb_client(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = rc_code['result_list']
    return send_response(output, store, "Veranstaltung_Berater.csv")


@bp.route("/ax-qy-visiter-last/<store>", methods=['GET'])
def ax_qy_visiter_last(store):
    sql_file = "qy_visiter_event_last.sql"
    if store == 'store-yes':
        rc_code = db_collect(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = "KundenNr;Nachname;Vorname;Anzahl_Besuche;Letzter_Besuch;Telefon;EMail\n"
        for row in rc_code['result_list']:
            (kd, n, v, an, ld, t, e) = row
            output += f"{kd};{n};{v};{an};{ld};{t};{e}\n"
    else:
        rc_code = mariadb_client(sql_file)
        if rc_code['status'] == 'ERR':
            abort(500)
        output = rc_code['result_list']
    return send_response(output, store, "Besucher_Letztes_Datum.csv")


def db_collect(sql_file):
    rc_code = {'status':'OK'}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor()
        os_file = open(current_app.root_path + '/sql/' + sql_file, 'r')
        cur.execute(os_file.read())
        os_file.close()
        rc_code['result_list'] = cur.fetchall()
        cur.close()
        db.close()
    except mariadb.PoolError as err:
        current_app.logger.error("Pool-Fehler: %s/ax_queries/%s", bp.name, err)
        rc_code['status'] = 'ERR'
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/ax_queries/%s", bp.name, err)
        rc_code['status'] = 'ERR'
    
    return rc_code


def mariadb_client(sql_file):
    rc_code = {'status':'OK'}
    command = f"/usr/bin/mariadb -u {credentials.Passwords.MYSQL_USER} -p'{credentials.Passwords.MYSQL_PWD}' -Bt -e 'source {current_app.root_path + '/sql/' + sql_file}' bv"
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, check=True, text=True)
        rc_code['result_list'] = result.stdout
    except subprocess.CalledProcessError as err:
        current_app.logger.error("Subprocess-Fehler: %s/ax_queries/%s", bp.name, err)
        rc_code['status'] = 'ERR'

    return rc_code


def send_response(output, store, file_name):
    resp = make_response(output)
    resp.content_encoding = "UTF-8"
    resp.automatically_set_content_length = True
    if store == 'store-yes':
        resp.mimetype = "text/csv"
        resp.default_mimetype = "text/csv"
        resp.headers['Content-Disposition']=f'attachment; filename="{file_name}"'
    else:
        resp.mimetype = "text/plain"
        resp.default_mimetype = "text/plain"
    resp.access_control_max_age = 0
    resp.headers['Cache-Control']='no-cache'
    resp.headers['Pragma']='no-cache'
    return resp

