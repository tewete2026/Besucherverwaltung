import mariadb
from flask import Blueprint
from flask import current_app, session
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import get_db, Configure, checkPermissions
from . import version

bp = Blueprint("verwBesucher", __name__)

@bp.route("/Verwalten-Besucher", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        abort(500)
    
    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT AnredeID as id,IFNULL(AnredeBezeichnung, 'keine Bestimmung') as bezeichnung from tAnrede ORDER BY Reihenfolge")
        dbdata.update({"anrede":cur.fetchall()})
        cur.close()
        db.close()
    except mariadb.PoolError as err:
        current_app.logger.error("Pool-Fehler: %s/%s", bp.name, err)
        abort(500)
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        abort(500)

    conf = Configure(request, current_app, session, title="Verwalten Besucher", header=["Besucherin/Besucher Kund.-Nr.", "Neue[n] Besucherin/Besucher erfassen"], prefix="02", app='visiter', 
                     link='link-verwbesucher', label="Besucher", category="Besucherin/Besucher", overview="Übersicht Besucherin/Besucher", pag_search="Suchbegriff eingeben")
    conf.javascript.add({'style_bg_visiter_wl':current_app.config["style-bg-visiter-wl"]})
    
    checkPermissions(conf)

    return render_template("verwBesucher.html", dbdata=dbdata, credits=conf.credits, conf=conf, javascript=conf.javascript.getOut())

