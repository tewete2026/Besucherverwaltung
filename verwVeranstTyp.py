import mariadb
from flask import Blueprint
from flask import current_app
from flask import request
from flask import render_template
from flask import redirect, url_for
from .db import Configure
from . import version

bp = Blueprint("verwVeranstTyp", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.route("/Verwalten-VeranstTyp", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))

    conf = Configure(request, current_app, title="Verwalten Veranstaltungsarten", header=["Veranstaltungsart Nr.", "Neue Veranstaltungsart erfassen"], prefix="06", app='veransttyp',
                     link='link-verwveransttyp', label="Veranstaltungsart", category="Veranstaltungsarten", overview="Übersicht Veranstaltungsarten", pag_search="oder Suchbegriff eingeben")

    return render_template("verwVeranstTyp.html", conf=conf, javascript=conf.javascript.getOut())

