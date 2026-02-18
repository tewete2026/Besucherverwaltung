import mariadb
from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import get_db, Configure
from . import version

bp = Blueprint("verwBerater", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.after_app_request
def add_security_headers(response):
    response.headers['Cache-Control']='no-cache'
    response.headers['Pragma']='no-cache'
    return response

@bp.route("/Verwalten-Berater", methods=['GET', 'POST'])
def main():
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

        cur.execute("SELECT id,bezeichnung FROM tGeraete ORDER BY bezeichnung")
        dbdata.update({"devices":cur.fetchall()})

        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        abort(500)

    conf = Configure(request, current_app, title="Verwalten Berater", header=["Beraterin/Berater Nr.", "Neuen Beraterin/Berater erfassen"], prefix="03", app='coaches',
                     link='link-verwberater', label="Berater", category="Beraterin/Berater", overview="Übersicht Beraterin/Berater", pag_search="oder Suchbegriff eingeben")

    return render_template("verwBerater.html", dbdata=dbdata, conf=conf, javascript=conf.javascript.getOut())

