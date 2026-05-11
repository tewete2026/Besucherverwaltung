import mariadb, hashlib
from flask import Blueprint
from flask import current_app
from flask import request, make_response, session
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .db import get_db, get_config
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
    loggedInCK = get_config('COOKIE_LOGIN', is_cookie=True)
    if loggedInCK in request.cookies: mode = 'yes'
    else: mode = 'no'

    dbdata={'status':'OK'}
    error={'class':'d-none'}
    if request.method == "POST" and mode == 'no':
        form_data = request.form
        if 'username' in form_data and 'password' in form_data:
            hash_value = hashlib.sha256(form_data['password'].encode())
            hashed_password = hash_value.hexdigest()
            try:
                db = get_db()
                if not db:
                    raise mariadb.PoolError()
                cur = db.cursor(dictionary=True)

                cur.execute("SELECT Vorname,Nachname,authMods from tBerater where username=? && password=?", (form_data['username'], hashed_password))
                result = cur.fetchone()
                if cur.rowcount < 1:
                    dbdata['status'] = 'NotFound'
                else:
                    dbdata['authMods'] = result['authMods']
                    dbdata['Vorname'] = result['Vorname']
                    dbdata['Nachname'] = result['Nachname']
                cur.close()
                db.close()
            except mariadb.PoolError as err:
                current_app.logger.error("Pool-Fehler: %s/%s", bp.name, err)
                abort(500)
            except mariadb.Error as err:
                db.close()
                current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
                abort(500)
            if dbdata['status'] == 'NotFound':
                error['userfault'] = "Benutzername und Passwort nicht vorhanden."
                error['class'] = ''
            else: 
                session['authMods'] = dbdata['authMods']
                session['coach_name'] = dbdata['Vorname'] + " " + dbdata['Nachname']
                resp = make_response(redirect(session['last-uri']))
                # resp.set_cookie(loggedInCK, 'true', max_age=(60*60*24*360), path=session['last-modname'])
                resp.set_cookie(loggedInCK, 'true', max_age=(60*60*24*5), path=session['last-modname'])
                return resp
    
    return render_template("signIn.html", mode=mode, error=error)


@bp.route("/logout", methods=['GET'])
def logout():
    loggedInCK = get_config('COOKIE_LOGIN', is_cookie=True)
    resp = make_response(redirect(url_for('main.index')))
    resp.delete_cookie(loggedInCK, path=session['last-modname'])
    session['authMods'] = None
    session['coach_name'] = None
    session['last-uri'] = None
    return resp
