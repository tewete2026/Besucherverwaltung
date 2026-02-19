import mariadb
from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template
from flask import redirect, url_for
from .db import Configure
from . import version

bp = Blueprint("verwThemen", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.after_app_request
def add_security_headers(response):
    response.headers['Cache-Control']='no-cache'
    response.headers['Pragma']='no-cache'
    return response

@bp.route("/Verwalten-Themen", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))

    conf = Configure(request, current_app, title="Verwalten Themen", header=["Thema Nr.", "Neues Thema erfassen"], prefix="05", app='themen',
                     link='link-verwthemen', label="Themen", category="Themen", overview="Übersicht Themen", pag_search="oder Titel eingeben")

    return render_template("verwThemen.html", conf=conf, javascript=conf.javascript.getOut())

