import mariadb
from flask import Blueprint
from flask import current_app, session
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import Configure, checkPermissions
from . import version

bp = Blueprint("verwVeranstTyp", __name__)

@bp.route("/Verwalten-VeranstTyp", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        abort(500)

    conf = Configure(request, current_app, session, title="Verwalten Veranstaltungsarten", header=["Veranstaltungsart Nr.", "Neue Veranstaltungsart erfassen"], prefix="06", app='veransttyp', 
                     link='link-verwveransttyp', label="Veranstaltungsart", category="Veranstaltungsarten", overview="Übersicht Veranstaltungsarten", pag_search="Suchbegriff eingeben")
    
    checkPermissions(conf)

    return render_template("verwVeranstTyp.html", conf=conf, javascript=conf.javascript.getOut())

