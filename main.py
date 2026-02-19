import mariadb
from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import get_db, Javascript, Configure
from . import version

bp = Blueprint("main", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.after_app_request
def add_security_headers(response):
    response.headers['Cache-Control']='no-cache'
    response.headers['Pragma']='no-cache'
    return response

@bp.route("/kommtNoch")
def kommtNoch():
    """Ein Dummy-Eintrag für ein Tool, das noch nicht erstellt ist."""
    return render_template("kommtNoch.html")

@bp.route("/")
def index():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))
    
    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT id,thema as bezeichnung FROM tThemen ORDER BY thema")
        dbdata.update({"themes":cur.fetchall()})

        cur.execute("SELECT id,bezeichnung,IFNULL(MaxBesucher,-1) as MaxBes,IFNULL(MaxBesucher,'--') as MaxBesucher FROM tOrte ORDER BY bezeichnung")
        dbdata.update({"targets":cur.fetchall()})

        cur.execute("SELECT id,bezeichnung FROM tVeranstTyp ORDER BY bezeichnung")
        dbdata.update({"types":cur.fetchall()})

        cur.execute("SELECT id,vorname,nachname,IF(aktiv=0,'-','(Beratung)') as aktiv,IF(tdm=0,'-','(Tdm)') as tdm,IF(berext=0,'-','(Externe Beratung)') as berext FROM tBerater ORDER BY nachname,vorname")
        dbdata.update({"coaches":cur.fetchall()})

        cur.execute("SELECT id,bezeichnung FROM tGeraete ORDER BY bezeichnung")
        dbdata.update({"devices":cur.fetchall()})

        cur.close()

        # outstr=f"Result of {cur.rowcount} entries:"
        # numresult=enumerate(result, start=1)
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        abort(500)

    conf = Configure(request, current_app, title="Verwalten Veranstaltungen", header=["Veranstaltung Nr.", "Neue Veranstaltung erfassen"], prefix="01", app='events',
                     link='link-main', label="Veranstaltungen", category="Veranstaltung", overview="Übersicht Veranstaltungen", pag_search="oder Datum-bis eingeben", pag_type="date")

    vis_max_arr = []
    for vis_elem in dbdata["targets"]:
        vis_max_arr.append([str(vis_elem["id"]), vis_elem["MaxBes"]])

    conf.javascript.add({'devices':Javascript.toOptions(dbdata.get("devices")), 'themes':Javascript.toOptions(dbdata.get("themes"))})
    conf.javascript.add({'max_visiters':vis_max_arr, 'style_bg_visiter_wl':current_app.config["style-bg-visiter-wl"]})

    return render_template("index.html", dbdata=dbdata, conf=conf, javascript=conf.javascript.getOut())

