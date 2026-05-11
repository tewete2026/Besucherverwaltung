import mariadb
from flask import Blueprint
from flask import current_app, session
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import get_db, Configure, get_config, get_session_entry
from . import version

bp = Blueprint("verwBerater", __name__)

@bp.route("/Verwalten-Berater", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        return redirect(url_for("internal_server_error"))

    conf = Configure(request, current_app, title="Verwalten Berater", header=["Beraterin/Berater Nr.", "Neuen Beraterin/Berater erfassen"], prefix="03", app='coaches', username=session['coach_name'],
                     link='link-verwberater', label="Berater", category="Beraterin/Berater", overview="Übersicht Beraterin/Berater", pag_search="Suchbegriff eingeben")
    
    usedMods = get_session_entry('authMods', as_dict=True)
    valid_mod = 0
    if conf.prefix in usedMods: valid_mod = usedMods[conf.prefix][1]
    conf.javascript.add({'valid_Mod':valid_mod})

    usedAllMods = get_config('used-modules', as_dict=True)
    mod_list = []
    for pref, mods in usedAllMods.items():
        (mod, active) = mods
        if active == 1: checked = 'checked'
        else: checked = ''
        mod_list.append([pref, mod, checked])
    conf.mod_list = mod_list
    conf.javascript.add({'used_mods':get_config('used-modules')})

    return render_template("verwBerater.html", conf=conf, javascript=conf.javascript.getOut())

