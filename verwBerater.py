import mariadb
from flask import Blueprint
from flask import current_app, session
from flask import request
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from .db import Configure, get_config, checkPermissions
from . import version

bp = Blueprint("verwBerater", __name__)

@bp.route("/Verwalten-Berater", methods=['GET', 'POST'])
def main():
    if current_app.config["NO_POOL_AVAILABLE"]:
        abort(500)

    conf = Configure(request, current_app, session, title="Verwalten Berater", header=["Beraterin/Berater Nr.", "Neue[n] Beraterin/Berater erfassen"], prefix="03", app='coaches', 
                     link='link-verwberater', label="Berater", category="Beraterin/Berater", overview="Übersicht Beraterin/Berater", pag_search="Suchbegriff eingeben")
    
    checkPermissions(conf)

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

