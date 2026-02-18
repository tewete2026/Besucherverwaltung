import mariadb
from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template
from flask import redirect, url_for
from .db import Configure
from . import version

bp = Blueprint("verwOrte", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.after_app_request
def add_security_headers(response):
    response.headers['Cache-Control']='no-cache'
    response.headers['Pragma']='no-cache'
    return response

@bp.route("/Verwalten-Orte", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))

    conf = Configure(request, current_app, title="Verwalten Orte", header=["Ort Nr.", "Neuen Ort erfassen"], prefix="07", app='targets',
                     link='link-verwveranstort', label="Orte", category="Orte", overview="Übersicht Orte", pag_search="oder Suchbegriff eingeben")

    return render_template("verwOrte.html", conf=conf, javascript=conf.javascript.getOut())

