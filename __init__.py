import os
from flask import Flask, url_for, send_from_directory
from flask import render_template, g, current_app, session, redirect, request
from logging.config import dictConfig
from . import version, credentials, db

def create_app(test_config="DEV"):
    """Create and configure an instance of the Flask application.
       First config the logger"""
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }, 'mail': {
            'format': '[%(asctime)s] in %(module)s: %(message)s',
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            "file1": {
                "class": "logging.handlers.RotatingFileHandler",
                "maxBytes": 1048576,
                "backupCount": 10,
                "filename": f"/var/log/python/{version.Configs.APP_NAME}.log",
                "formatter": "default"
            },
            "file2": {
                "class": "logging.handlers.RotatingFileHandler",
                "maxBytes": 1048576,
                "backupCount": 10,
                "filename": f"/var/log/python/{version.Configs.APP_NAME}_ERR.log",
                "formatter": "default",
                'level': 'ERROR'
            },
            "smtp": {
                "class": "logging.handlers.SMTPHandler",
                "mailhost": ("localhost",25),
                "fromaddr": f"{version.Configs.APP_NAME}-noreply@pcafe-webserver.local",
                "toaddrs": credentials.EMails.SMTPHandler,
                "subject": "Flask-Mail-Handler",
                "formatter": "mail",
                'level': 'ERROR'
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'file1', 'file2', 'smtp']
        }
    })
    app = Flask(version.Configs.APP_NAME, instance_relative_config=False, static_url_path="/src")
    if test_config == "DEV":
        modname = "/"
    else:
        modname = f"/{version.Configs.APP_NAME}"
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY=credentials.Passwords.SECRET_KEY,
        SESSION_COOKIE_NAME="drk-bv-session",
        SESSION_COOKIE_PATH=modname,
        TS=db.TimeSet("Europe/Berlin"),
        HOSTNAME=os.uname().nodename,
        TEST_RUN=False,
        DB_POOL=None,
        NO_POOL_AVAILABLE=False,
        COOKIE_PREFIX='drk-bv-',
        COOKIE_LOGIN='is-logged-in-TEST'
    )

    @app.before_request
    def check_login():
        if request.method == 'GET' and not db.get_config('COOKIE_LOGIN', is_cookie=True) in request.cookies:
            lurl = request.url.rsplit('/')
            uri = lurl.pop()
            ind = ["store-no", "store-yes"].count(uri)
            if ind > 0:
                uri = f"{lurl.pop()}/{uri}"
            if current_app.config['TEST_RUN']: module = ''
            else: module = lurl.pop()
            if len(uri) > 0 and not uri.startswith('nc-'):
                found = False
                for suffix in ['.css', '.jpg', '.js', '.png']:
                    if uri.endswith(suffix): found = True
                if not found:
                    if len(module) == 0: last_uri = '/' + uri
                    else: last_uri = '/' + module + '/' + uri
                    session['last-modname'] = '/' + module
                    if uri != 'login':
                        session['last-uri'] = last_uri
                        return redirect(url_for('login.login'))
                    else:
                        if not 'last-uri' in session: session['last-uri'] = '/' + module

    @app.after_request
    def add_several_headers(response):
        response.headers['Cache-Control']='no-cache'
        response.headers['Pragma']='no-cache'
        return response

    @app.route("/")
    def index():
        return redirect(url_for('main.index'))

    @app.route("/favicon.ico")
    def favicon():
        path = current_app.root_path + '/static'
        return send_from_directory(path, 'Favicon_PCafe.png')

    @app.route("/nc-short-view")
    def nc_short_view():
        credits = {
            "created":version.Configs.APP_CREATED,
            "version":version.Configs.APP_VERSION,
            "author":version.Configs.APP_AUTHOR,
            "headline":"Übersicht"
        }
        return render_template("starter.html", credits=credits)

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        credits = {
            "created":version.Configs.APP_CREATED,
            "version":version.Configs.APP_VERSION,
            "author":version.Configs.APP_AUTHOR,
            "headline":"Seite nicht gefunden"
        }
        return render_template('pageNotFound.html', credits=credits), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        # note that we set the 500 status explicitly
        credits = {
            "created":version.Configs.APP_CREATED,
            "version":version.Configs.APP_VERSION,
            "author":version.Configs.APP_AUTHOR,
            "headline":"Interner Fehler"
        }
        return render_template('internalError.html', credits=credits), 500

    @app.errorhandler(405)
    def method_not_valid(e):
        # note that we set the 405 status explicitly
        credits = {
            "created":version.Configs.APP_CREATED,
            "version":version.Configs.APP_VERSION,
            "author":version.Configs.APP_AUTHOR,
            "headline":"Keine Berechtigung"
        }
        return render_template('internalError.html', credits=credits), 405
    
    @app.teardown_appcontext
    def teardown_db(exception):
        if 'DB_ID' in g:
            db_id = g.pop('DB_ID')
            for id, conn in db_id.items():
                conn.reset()
                current_app.logger.debug("Connection-ID %s cleared at end of context", id)

    app.logger.info("Name=%s; Version detected=%s; Created=%s", version.Configs.APP_NAME, version.Configs.APP_VERSION, version.Configs.APP_CREATED)
    app.logger.info("Root-Path=%s", app.root_path)

    if test_config == "DEV":
        app.config.from_mapping(TEST_RUN=True)
        app.logger.info("Test-Dev active; Logger=%s; Parent-Logger=%s", app.logger.name, app.logger.parent.name)
        for hdlr in app.logger.parent.handlers:
            if hdlr.get_name() == "smtp":
                app.logger.parent.removeHandler(hdlr)
                app.logger.debug("Handler %s aus %s entfernt.", hdlr.get_name(), app.logger.parent.name)
    else:
        app.logger.info("Production active")

    # register the database commands
    with app.app_context():
        if db.init_app(app) == "ERR":
            app.config.from_mapping(NO_POOL_AVAILABLE=True)

    ts = app.config["TS"]
    ts.setRecordunlock(int(app.config["wait-for-unlock-record"]))

    # apply the blueprints to the app
    from . import main,login,ax_visiter,ax_events,ax_coaches,ax_eventtypes,ax_themes,ax_targets,ax_default,ax_queries,yx_gen_service,verwBesucher,verwBerater,verwVeranstTyp,verwThemen,verwOrte
    app.register_blueprint(main.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(ax_visiter.bp)
    app.register_blueprint(ax_events.bp)
    app.register_blueprint(ax_coaches.bp)
    app.register_blueprint(ax_eventtypes.bp)
    app.register_blueprint(ax_themes.bp)
    app.register_blueprint(ax_targets.bp)
    app.register_blueprint(ax_default.bp)
    app.register_blueprint(ax_queries.bp)
    app.register_blueprint(yx_gen_service.bp)
    app.register_blueprint(verwBesucher.bp)
    app.register_blueprint(verwBerater.bp)
    app.register_blueprint(verwVeranstTyp.bp)
    app.register_blueprint(verwThemen.bp)
    app.register_blueprint(verwOrte.bp)
    
    app.logger.debug(f"Registered Blueprint Count: {len(app.blueprints.items())}")
    for bp_name, blpr in app.blueprints.items():
        app.logger.debug(f"Registered Blueprint: {bp_name}, {blpr.import_name}, {blpr.url_prefix}, {blpr.root_path}")
    for hdlr in app.logger.parent.handlers:
        app.logger.debug("Registered Handler in %s: %s", app.logger.parent.name, hdlr.get_name())

    app.add_url_rule("/", view_func=index)

    return app
