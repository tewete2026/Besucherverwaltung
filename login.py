import mariadb, hashlib
from flask import Blueprint
from flask import current_app
from flask import request, session
from flask import render_template
from flask import redirect, url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .db import get_db
from . import version

bp = Blueprint("login", __name__)


@bp.route("/login", methods=['GET', 'POST'])
def login():
    ts = current_app.config["TS"]
    if current_app.config["NO_POOL_AVAILABLE"]:
        abort(500)
    session.permanent = True
    if 'login_name' in session: is_loggedin = 'yes'
    else: is_loggedin = 'no'

    dbdata={'status':'OK'}
    error={'class':'d-none'}
    if request.method == "POST" and is_loggedin == 'no':
        form_data = request.form
        if 'username' in form_data and 'password' in form_data:
            hash_value = hashlib.sha256(form_data['password'].encode())
            hashed_password = hash_value.hexdigest()
            try:
                db = get_db()
                if not db:
                    raise mariadb.PoolError()
                cur = db.cursor(dictionary=True)

                # cur.execute("SELECT Vorname,Nachname,authMods from tBerater where username=? && password=?", (form_data['username'].lower(), hashed_password))
                # Temporär zunächst ohne Passwort
                cur.execute("SELECT Vorname,Nachname,authMods from tBerater where username=?", (form_data['username'].lower(),))
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
                session['login_name'] = dbdata['Vorname'] + " " + dbdata['Nachname']
                return redirect(session['last-uri'])
    
    credits = {}
    credits['version'] = f"{version.Configs.APP_VERSION} - {version.Configs.APP_CREATED}"
    if is_loggedin == 'yes': credits['username'] = session['login_name']
    return render_template("signIn.html", mode=is_loggedin, error=error, credits=credits)


@bp.route("/logout", methods=['GET'])
def logout():
    session.clear()
    # session.pop('login_name', None)
    # session.pop('authMods', None)
    # session.pop('last-uri', None)
    return redirect(url_for('main.index'))
