import mariadb, hashlib
from flask import Blueprint, current_app
from .db import get_db
from . import tools

bp = Blueprint("yx_gen_service", __name__)


@bp.route("/yx-reload-config/", methods=['GET'])
def yx_reload_config():
    rc_code = {"status":"OK"}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        db.begin()
        cur = db.cursor()
        """ Einlesen Konfigurations-Elemente aus der Datenbanktabelle _Config """
        cur.execute("select item,value from _Config order by id")
        result = cur.fetchall()
        current_app.config.update(result)
        rc_code["Number Rows"] = len(result)
        for entry in result:
            (k, v) = entry
            rc_code[k] = v
            current_app.logger.debug("Relod Config: %s=%s", k, v)
        db.commit()
        cur.close()
        db.close()
    except mariadb.PoolError as err:
        rc_code["status"] = "ERR"
        rc_code["message"] = "Datenbankfehler: {}".format(err)
    except mariadb.Error as err:
        rc_code["status"] = "ERR"
        rc_code["message"] = "Datenbankfehler: {}".format(err)
        db.rollback()
        db.close()

    return rc_code



@bp.route("/yx-gen-berater-passwd/", methods=['GET'])
def yx_gen_berater_passwd():
    c_list = {
        7:["Kuhrt", "3871", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        8:["Meyer-Wiechmann", "1942", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        21:["Wachler-Thomsen", "8461", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        23:["Kühl", "5391", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        26:["Düßler", "2741", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        29:["Härtling", "2931", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        31:["Schulte", "3744", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        39:["Eilhardt", "2261", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        40:["Kamann", "2819", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        44:["Lorenzen", "8923", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        51:["Oldag", "9171", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        52:["Plat", "2425", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        53:["Scherf", "3738", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        56:["Beyer", "9391", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        57:["Porsch", "2855", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        58:["Luther", "5621", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        59:["Schumacher", "8292", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        60:["Becker", "9911", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        61:["Münch", "2288", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        62:["Bülow", "6723", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        64:["Torres", "7632", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        65:["Prosch", "9278", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
        66:["Aurast", "9897", '[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",1]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",1]],["07",["Veranstaltungsorte",1]]]'],
    }
    rc_code = {'status':"OK"}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        db.begin()
        cur = db.cursor(dictionary=True)
        for c_id, c_name in c_list.items():
            hash_value = hashlib.sha256(c_name[1].encode())
            hashed_password = hash_value.hexdigest()
            cur.execute("UPDATE tBerater set username=?, authMods=?, password=? WHERE id=?", (c_name[0].lower(), c_name[2], hashed_password, c_id))
            c_name.append(cur.rowcount)
            c_name.append(hashed_password)
        rc_code['db_data'] = c_list

        db.commit()
        cur.close()
        db.close()
    except mariadb.PoolError as err:
        rc_code['status'] = "ERR - Datenbankfehler: {}".format(err)
    except mariadb.Error as err:
        rc_code['status'] = "ERR - Datenbankfehler: {}".format(err)
        db.rollback()
        db.close()

    return rc_code


@bp.route("/yx-gen-init-wl/", methods=['GET'])
def yx_gen_init_wl():
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        db.begin()
        cur_i = db.cursor()
        cur_o = db.cursor(dictionary=True)

        cur_i.execute("SELECT DISTINCT VeranstID FROM tBesuche group by VeranstID order by VeranstID")
        rc_wl = tools.setVisiterWL(cur_o, cur_i.fetchall(), True)

        db.commit()
        cur_i.close()
        cur_o.close()
        db.close()
    except mariadb.PoolError as err:
        rc_code = "ERR - Pool-Fehler: {}".format(err)
    except mariadb.Error as err:
        rc_code = "ERR - Datenbank.Fehler: {}".format(err)
        db.rollback()
        db.close()

    return "\n".join(["<!DOCTYPE html>",
            "<html lang='de-de'>",
            "    <head>",
            "        <title>Ende des Prozesses</title>",
            "        <style>",
            "            body {font-family:sans-serif}",
            "        </style>",
            "    </head>",
            "    <body>",
            "        <h2>Ergebnis des Prozesses:  " + rc_wl + "</h2>",
            "    </body>",
            "</html>"])
