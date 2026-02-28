import mariadb, sys
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request

from .db import get_db
from .ax_default import mx_get_overview, mx_submit_release, mx_get_edit
from . import version

bp = Blueprint("ax_eventtypes", __name__, url_prefix=f"/{version.Configs.APP_NAME}")


@bp.route("/ax-get-veransttyp-edit/", methods=['POST'])
def ax_get_veransttyp_edit():
    return mx_get_edit(request, current_app, table_name="tVeranstTyp", data_key="veransttyp", select_field="Bezeichnung")


@bp.route("/ax-get-veransttyp-overview/", methods=['POST'])
def ax_get_veransttyp_overview():
    rc_code = mx_get_overview(request, current_app, html_template_body="verwVeranstTyp_body.html", 
                              sql=["SELECT a.id,a.Bezeichnung from tVeranstTyp a", "ORDER BY a.Bezeichnung"], search_field=["a.Bezeichnung"])
    return rc_code


@bp.route("/ax-submit-veransttyp-release/", methods=['POST'])
def ax_submit_veransttyp_release():
    rc_code = mx_submit_release(request, current_app, table_name="tVeranstTyp")
    return rc_code


@bp.route("/ax-submit-veransttyp/", methods=['POST'])
def ax_submit_veransttyp():
    result = request.get_json()
    current_app.logger.info("Empfangene Daten: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "id":"(Neu)", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}

    try:
        item_id = None
        item_timestamp = None
        for pkey, parm in result:
            if pkey == "bezeichnung":
                type_bezeichnung = parm
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
                cur.execute("SELECT IFNULL(sperre,'INVALID') as sperre FROM tVeranstTyp WHERE id=? FOR UPDATE", (item_id,))
                row_data = cur.fetchone()
                timestamp = str(row_data["sperre"])
                if timestamp == item_timestamp:
                    cur.execute("update tVeranstTyp set sperre=null,Bezeichnung=? where id=?", (type_bezeichnung, item_id))
                elif timestamp == "INVALID":
                    update_allowed = False
                    rc_code["status"] = "INVALID"
                else:
                    update_allowed = False
                    rc_code["status"] = "NOTALWD"
            else:
                cur.execute("insert into tVeranstTyp(Bezeichnung) values(?)", (type_bezeichnung,))
                last_id = cur.lastrowid
                rc_code["id"] = last_id

            if update_allowed:
                if item_id is not None:
                    current_app.logger.info("Datensatz aktualisiert: ID=%s, Bezeichnung=%s", last_id, type_bezeichnung)
                    rc_code["mode"] = "CHG"
                else:
                    current_app.logger.info("Datensatz hinzugefügt: ID=%s, Bezeichnung=%s", last_id, type_bezeichnung)
                    rc_code["mode"] = "INS"
            db.commit()
            cur.close()
            db.close()
        except mariadb.IntegrityError as err:
            rc_code["status"] = "DBL"
            current_app.logger.warning("Datenbank-doppelter Eintrag: %s/ax-submit-veransttyp/%s", bp.name, err)
            db.rollback()
            db.close()
            current_app.logger.warning("Datenbank-Rollback-doppelter Eintrag")
        except mariadb.Error as err:
            current_app.logger.error("Datenbank-Fehler: %s/ax-submit-veransttyp/%s", bp.name, err)
            rc_code["status"] = "ERR"
            db.rollback()
            db.close()
            current_app.logger.error("Datenbank-Rollback")
    except:
        (type, value, traceback) = sys.exc_info()
        current_app.logger.critical("Unexpected error: Type=%s; Exception=%s; Trace-Line=%s",type, value, traceback.tb_lineno)
        rc_code["status"] = "ERR"

    return rc_code
