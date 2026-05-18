import mariadb
from flask import Blueprint
from flask import current_app, session
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import Configure, checkPermissions
from . import version

bp = Blueprint("verwThemen", __name__)

@bp.route("/Verwalten-Themen", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        abort(500)

    conf = Configure(request, current_app, session, title="Verwalten Themen", header=["Thema Nr.", "Neues Thema erfassen"], prefix="05", app='theme', 
                     link='link-verwthemen', label="Themen", category="Themen", overview="Übersicht Themen", pag_search="Titel eingeben")
    
    checkPermissions(conf)

    return render_template("verwThemen.html", conf=conf, javascript=conf.javascript.getOut())

