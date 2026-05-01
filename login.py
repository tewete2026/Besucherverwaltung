import mariadb, os
from flask import Blueprint
from flask import current_app
from flask import request, make_response, session
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .db import get_db
from . import version

bp = Blueprint("login", __name__)


@bp.after_request
def add_security_headers(response):
    response.headers['Cache-Control']='no-cache'
    response.headers['Pragma']='no-cache'
    return response


@bp.route("/login", methods=['GET', 'POST'])
def login():
    ts = current_app.config["TS"]
    if current_app.config["NO_POOL_AVAILABLE"]:
        abort(500)

    # cks_prefix = 'ax_submit_'
    # cks = ['last_id', 'last_kdnr', 'last_mode', 'submit_status', 'upload_status', 'can_replace', 'DB_Error']
    # rc_code = {}
    # for cks_key in cks:
    #     cks_value = cks_prefix + cks_key
    #     if cks_value in request.cookies: rc_code.update({cks_key:request.cookies[cks_value]})

    if request.method == "POST":
    #     size = duration = temp_name = target_name = None
    #     file = request.files['frm-main-file']
    #     filename = secure_filename(file.filename)
    #     if len(filename) > 0: 
    #         temp_name = current_app.instance_path + "/upload/" + filename
    #         target_name = current_app.instance_path + "/long/" + filename
    #         file.save(temp_name)
    #         # (title, mp3description, published, size, duration, chapter) = getMP3Info(temp_name)
    #         (size, duration) = getMpegInfo(temp_name)
    #     rc_code = ax_submit_episode(request.form, filename, target_name, size, duration)
    #     if rc_code["submit_status"] == "OK":
    #         if target_name is not None:
    #             if 'can_replace' in rc_code:
    #                 can_replace = rc_code['can_replace']
    #             else: can_replace = True
    #             if can_replace:
    #                 os.replace(temp_name, target_name)
    #                 rc_code["upload_status"] = filename
    #     else:
    #         if temp_name is not None and os.path.exists(temp_name):
    #             os.remove(temp_name)

        print(session['last-uri'], session['last-modname'])
        resp = make_response(redirect(session['last-uri']))
        # resp.set_cookie(current_app.config['COOKIE_PREFIX'] + '-is-logged-in', 'true', max_age=(60*60*24*360), path=session['last-modname'])
        resp.set_cookie(current_app.config['COOKIE_PREFIX'] + '-is-logged-in-TEST', 'true', max_age=(60*60*24*5), path=session['last-modname'])
        return resp

    # try:
    #     db = get_db()
    #     if not db:
    #         raise mariadb.PoolError()
    #     cur = db.cursor(dictionary=True)

    #     cur.execute("SELECT MAX(kdnr)+1 as max_kdnr from tEpisode")
    #     max_kdnr = cur.fetchone()['max_kdnr']

    #     cur.close()
    #     db.close()
    # except mariadb.Error as err:
    #     db.close()
    #     current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
    #     abort(500)

    # conf = Configure(request, current_app, title="Verwalten Episoden", header=["Episode Nr.", "Neue Episode erfassen Nr. " + str(max_kdnr)], prefix="03", app='episode',
    #                  link='link-main', label="Episoden", category="Episoden", overview="Übersicht Episoden", pag_search="oder Titel eingeben", 
    #                  btn_type="submit")
    # conf.javascript.add({"form_submit":'yes'})
    # conf.append("title_default", "Folge {0:04.0f} in Woche {1:04.0f}/{2:02.0f}".format(max_kdnr, ts.isocalendar()[0], ts.isocalendar()[1]))
    # if rc_code: conf.javascript.add(rc_code)

    # return render_template("service/verwEpisoden.html", conf=conf, javascript=conf.javascript.getOut())
    
    if current_app.config['COOKIE_PREFIX'] + '-is-logged-in-TEST' in request.cookies: mode = 'yes'
    else: mode = 'no'
    
    return render_template("signIn.html", mode=mode)
