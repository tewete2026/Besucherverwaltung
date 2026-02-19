import os
from flask import Flask, url_for
from flask import render_template
from logging.config import dictConfig
from . import version, credentials
from .db import TimeSet

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
                "mailhost": ("localhost",825),
                "fromaddr": f"{version.Configs.APP_NAME}-noreply@tewete.de",
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
    app = Flask(version.Configs.APP_NAME, instance_relative_config=True, static_url_path=f"/{version.Configs.APP_NAME}/src")
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY=credentials.Passwords.SECRET_KEY,
        TS=TimeSet("Europe/Berlin"),
        HOSTNAME = os.uname().nodename,
        TEST_RUN=False,
        DB_POOL=None,
        NO_POOL_AVAILABLE=False
    )

    @app.route("/")
    def default():
        return render_template("starter.html")

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return render_template('pageNotFound.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        # note that we set the 500 status explicitly
        return render_template('internalError.html'), 500

    @app.errorhandler(405)
    def method_not_valid(e):
        # note that we set the 500 status explicitly
        return render_template('internalError.html'), 500

    app.logger.info("Name=%s; Version detected=%s; Created=%s", version.Configs.APP_NAME, version.Configs.APP_VERSION, version.Configs.APP_CREATED)

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
    from . import db
    if db.init_app(app) == "ERR":
        app.config.from_mapping(NO_POOL_AVAILABLE=True)

    ts = app.config["TS"]
    ts.setRecordunlock(int(app.config["wait-for-unlock-record"]))

    # apply the blueprints to the app
    from . import main,ax_visiter,ax_events,ax_coaches,ax_devices,ax_eventtypes,ax_themes,ax_targets,ax_default,yx_gen_service,verwBesucher,verwBerater,verwVeranstTyp,verwThemen,verwGeraete,verwOrte
    app.register_blueprint(main.bp)
    app.register_blueprint(ax_visiter.bp)
    app.register_blueprint(ax_events.bp)
    app.register_blueprint(ax_coaches.bp)
    app.register_blueprint(ax_devices.bp)
    app.register_blueprint(ax_eventtypes.bp)
    app.register_blueprint(ax_themes.bp)
    app.register_blueprint(ax_targets.bp)
    app.register_blueprint(ax_default.bp)
    app.register_blueprint(yx_gen_service.bp)
    app.register_blueprint(verwBesucher.bp)
    app.register_blueprint(verwBerater.bp)
    app.register_blueprint(verwVeranstTyp.bp)
    app.register_blueprint(verwThemen.bp)
    app.register_blueprint(verwGeraete.bp)
    app.register_blueprint(verwOrte.bp)
    
    app.logger.debug(f"Registered Blueprint Count: {len(app.blueprints.items())}")
    for bp_name, blpr in app.blueprints.items():
        app.logger.debug(f"Registered Blueprint: {bp_name}, {blpr.import_name}, {blpr.url_prefix}, {blpr.root_path}")
    for hdlr in app.logger.parent.handlers:
        app.logger.debug("Registered Handler in %s: %s", app.logger.parent.name, hdlr.get_name())

    app.add_url_rule(f"/{version.Configs.APP_NAME}/", view_func=main.index)

    return app
