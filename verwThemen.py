import mariadb
from flask import Blueprint
from flask import current_app, session
from flask import request
from flask import render_template
from flask import redirect, url_for
from .db import Configure, get_session_entry
from . import version

bp = Blueprint("verwThemen", __name__)

@bp.route("/Verwalten-Themen", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))

    conf = Configure(request, current_app, title="Verwalten Themen", header=["Thema Nr.", "Neues Thema erfassen"], prefix="05", app='theme', username=session['coach_name'],
                     link='link-verwthemen', label="Themen", category="Themen", overview="Übersicht Themen", pag_search="Titel eingeben")
    
    usedMods = get_session_entry('authMods', as_dict=True)
    valid_mod = 0
    if conf.prefix in usedMods: valid_mod = usedMods[conf.prefix][1]
    conf.javascript.add({'valid_Mod':valid_mod})

    return render_template("verwThemen.html", conf=conf, javascript=conf.javascript.getOut())

