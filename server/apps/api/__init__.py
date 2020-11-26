# -*- coding: utf-8 -*-

import os
from datetime import timedelta

from flask import Flask, jsonify

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from server.conf import setup_conf
from server.extensions import cache, db, executor, migrate


def create_app(app_env='production'):
    # set config
    CONF = setup_conf(app_env=app_env, app_kind='api')
    # setup_log(prefix="pip_info_api")

    # instantiate the app
    app = Flask(__name__)

    app.secret_key = CONF.myapp.secret_key
    app.permanent_session_lifetime = timedelta(days=15)

    app.config['SQLALCHEMY_DATABASE_URI'] = CONF.db.connection
    app.config['SQLALCHEMY_BINDS'] = {'ops_ticket': CONF.db.ops_ticket}
    app.config['SQLALCHEMY_POOL_SIZE'] = CONF.db.pool_size
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    @app.context_processor
    def default_context_processor():
        return {'title': CONF.myapp.title, 'baseurl': CONF.myapp.baseurl}

    register_extensions(app, CONF)
    register_blueprints(app)
    register_errorhandlers(app)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app


def register_extensions(app, CONF):
    """Register Flask extensions."""
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    sentry_sdk.init(dsn=CONF.sentry.dsn, integrations=[FlaskIntegration()])
    executor.init_app(app)
    if app_env == 'development':
        from flask_debugtoolbar import DebugToolbarExtension
        debug_toolbar = DebugToolbarExtension()
        debug_toolbar.init_app(app)
    return None


def register_blueprints(app):
    """register blueprints"""
    # from server.apps.api.main import main_bp
    # app.register_blueprint(main_bp)
    pass


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return jsonify({'code': error_code, 'msg': str(error)})

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


app_env = os.getenv('APP_ENV', 'production')
app = create_app(app_env)


def entry():
    app.run()
