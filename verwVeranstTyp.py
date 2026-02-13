import mariadb
from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template
from flask import redirect, url_for
from .db import Configure
from . import version

bp = Blueprint("verwVeranstTyp", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.after_app_request
def add_security_headers(response):
    response.headers['Cache-Control']='no-cache'
    response.headers['Pragma']='no-cache'
    return response

@bp.route("/Verwalten-VeranstTyp", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))

    conf = Configure("Verwalten Veranstaltungsarten", ["Veranstaltungsart Nr.", "Neue Veranstaltungsart erfassen"], "06", 'veransttyp', 'link-verwveransttyp', request, current_app)

    return render_template("verwVeranstTyp.html", modname=conf.modname, credits=conf.credits, avascript=conf.javascript.getOut())

