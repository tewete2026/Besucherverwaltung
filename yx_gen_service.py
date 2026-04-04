import mariadb
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



@bp.route("/yx-gen-berater-make/", methods=['GET'])
def yx_gen_berater_make():
    rc_code = "OK"
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        db.begin()
        cur_i = db.cursor(dictionary=True)
        cur_o = db.cursor(dictionary=True)

        cur_i.execute("SELECT id,berater1,berater2,berater3,berater4,berater5 FROM tVeranst order by id")
        while True:
            row = cur_i.next()
            if row:
                v_id = row["id"]
                v_ber = [row["berater1"], row["berater2"], row["berater3"], row["berater4"], row["berater5"]]
                for ber in v_ber:
                    if ber and ber.isnumeric():
                        cur_o.execute("insert into tBeraterVer(VeranstID,BeraterID) values(?,?)", (v_id, ber))
            else:
                break

        db.commit()
        cur_i.close()
        cur_o.close()
        db.close()
    except mariadb.PoolError as err:
        rc_code = "ERR - Datenbankfehler: {}".format(err)
    except mariadb.Error as err:
        rc_code = "ERR - Datenbankfehler: {}".format(err)
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
