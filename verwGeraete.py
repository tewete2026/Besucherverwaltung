import mariadb
from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template
from flask import redirect, url_for
from .db import Configure
from . import version

bp = Blueprint("verwGeraete", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.after_app_request
def add_security_headers(response):
    response.headers['Cache-Control']='no-cache'
    response.headers['Pragma']='no-cache'
    return response

@bp.route("/Verwalten-Geraete", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))

    conf = Configure(request, current_app, title="Verwalten Geräte", header=["Gerät Nr.", "Neues Gerät erfassen"], prefix="04", app='devices',
                     link='link-verwgeraete', label="Berater", category="Geräte", overview="Übersicht Geräte", pag_search="oder Suchbegriff eingeben")

    return render_template("verwGeraete.html", conf=conf, javascript=conf.javascript.getOut())

