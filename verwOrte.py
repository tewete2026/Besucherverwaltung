import mariadb
from flask import Blueprint
from flask import current_app, session
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import Configure, checkPermissions
from . import version

bp = Blueprint("verwOrte", __name__)

@bp.route("/Verwalten-Orte", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        abort(500)

    conf = Configure(request, current_app, session, title="Verwalten Orte", header=["Ort Nr.", "Neuen Ort erfassen"], prefix="07", app='targets', 
                     link='link-verwveranstort', label="Orte", category="Orte", overview="Übersicht Orte", pag_search="Suchbegriff eingeben")
    
    checkPermissions(conf)

    return render_template("verwOrte.html", conf=conf, javascript=conf.javascript.getOut())

