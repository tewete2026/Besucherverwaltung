import mariadb
from flask import Blueprint
from flask import current_app, session
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import get_db, Javascript, Configure, get_config, get_session_entry
from . import version

bp = Blueprint("main", __name__)


@bp.route("/kommtNoch")
def kommtNoch():
    """Ein Dummy-Eintrag für ein Tool, das noch nicht erstellt ist."""
    credits = {
        "created":version.Configs.APP_CREATED,
        "version":version.Configs.APP_VERSION,
        "author":version.Configs.APP_AUTHOR,
        "headline":"Die gewünschte Seite ist noch in Arbeit ...."
    }
    return render_template("kommtNoch.html", credits=credits)

@bp.route("/Exportieren")
def exports():
    credits = {
        "created":version.Configs.APP_CREATED,
        "version":version.Configs.APP_VERSION,
        "author":version.Configs.APP_AUTHOR,
        "headline":"Exportieren (Herunterladen) von Excel/CSV Listen"
    }
    return render_template("exports.html", credits=credits)

@bp.route("/Verwalten-Veranstaltungen")
def index():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))
    
    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT id,CONCAT(CASE GruppenID WHEN 10 THEN '✆' WHEN 20 THEN '✓' ELSE '✗' END,' - ',thema) as bezeichnung FROM tThemen ORDER BY GruppenID,thema")
        dbdata.update({"themes":cur.fetchall()})

        # cur.execute("SELECT id,bezeichnung,IFNULL(MaxBesucher,-1) as MaxBes,IFNULL(MaxBesucher,'--') as MaxBesucher FROM tOrte ORDER BY bezeichnung")
        cur.execute("SELECT id,bezeichnung FROM tOrte ORDER BY bezeichnung")
        dbdata.update({"targets":cur.fetchall()})

        cur.execute("SELECT id,bezeichnung FROM tVeranstTyp ORDER BY bezeichnung")
        dbdata.update({"types":cur.fetchall()})

        cur.execute("SELECT id,CONCAT(IF(Aktiv=1,'✓','✗'),' ',vorname,' ',nachname) as name FROM tBerater ORDER BY vorname,nachname")
        dbdata.update({"coaches":cur.fetchall()})

        cur.close()

        # outstr=f"Result of {cur.rowcount} entries:"
        # numresult=enumerate(result, start=1)
        db.close()
    except mariadb.PoolError as err:
        current_app.logger.error("Pool-Fehler: %s/%s", bp.name, err)
        abort(500)
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        abort(500)
    conf = Configure(request, current_app, title="Verwalten Veranstaltungen", header=["Veranstaltung Nr.", "Neue Veranstaltung erfassen"], prefix="01", app='events', username=session['coach_name'],
                     link='link-main', label="Veranstaltungen", category="Veranstaltung", overview="Übersicht Veranstaltungen", pag_search="oder Datum-bis", pag_type="date")
    
    usedMods = get_session_entry('authMods', as_dict=True)
    valid_mod = 0
    if conf.prefix in usedMods: valid_mod = usedMods[conf.prefix][1]
    conf.javascript.add({'valid_Mod':valid_mod})

    vis_max_arr = []
    # for vis_elem in dbdata["targets"]:
    #     vis_max_arr.append([str(vis_elem["id"]), vis_elem["MaxBes"]])

    conf.javascript.add({'max_visiters':vis_max_arr, 'style_bg_visiter_wl':current_app.config["style-bg-visiter-wl"]})
    conf.javascript.add({'style_bg_visiter_wl':current_app.config["style-bg-visiter-wl"]})

    return render_template("index.html", dbdata=dbdata, conf=conf, javascript=conf.javascript.getOut())

