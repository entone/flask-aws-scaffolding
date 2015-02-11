from flask import Flask, redirect, url_for, request, g
from flask_pjax import PJAX
from flask.ext.login import LoginManager, current_user
from flask.ext.session import Session
from flaskaws.models.client import Admin
from flaskaws import config
from flaskaws import db
from slugify import slugify
import humongolus
import logging
import time

class App(Flask):

    def __init__(self):
        super(App, self).__init__(__name__)
        self.config.from_object('flaskaws.config')
        logging.info("SERVER_NAME: {}".format(self.config['SERVER_NAME']))
        self.before_request(self.init_dbs)
        try:
            self.init_session()
            self.init_login()
            self.init_blueprints()
            self.init_pjax()
            self.init_templates()
        except Exception as e:
            logging.exception(e)

    def load_user(self, id):
        try:
            logging.info("Loading User: {}".format(id))
            a = Admin(id=id)
            return a
        except Exception as e:
            logging.exception(e)
            return None

    def init_templates(self):
        self.jinja_env.filters['slugify'] = slugify

    def configure_dbs(self):
        es = db.init_elasticsearch()
        db.create_index(es)
        influx = db.init_influxdb()
        db.create_shards(influx)

    def init_dbs(self):
        g.ES = db.init_elasticsearch()
        g.INFLUX = db.init_influxdb()
        g.MONGO = db.init_mongodb()
        humongolus.settings(logging, g.MONGO)

    def init_session(self):
        self.config['SESSION_MONGODB'] = db.init_mongodb()
        self.config['SESSION_MONGODB_DB'] = "app_sessions"
        self.config['SESSION_MONGODB_COLLECT'] = "sessions"
        Session(self)

    def init_login(self):
        self.login_manager = LoginManager()
        self.login_manager.init_app(self)
        self.login_manager.user_callback = self.load_user
        self.login_manager.login_view = "auth.login"

    def user_logged_in(self):
        logging.info(request.path)
        if not current_user.is_authenticated():
            return redirect(url_for("auth.login", next=request.path, _external=True))

    def init_pjax(self):
        PJAX(self)

    def init_blueprints(self):
        from controllers.dashboard import dashboard
        from controllers.auth import auth
        from controllers.auth.facebook import facebook
        from controllers.healthcheck import hc
        dashboard.before_request(self.user_logged_in)
        self.register_blueprint(dashboard)
        self.register_blueprint(auth)
        self.register_blueprint(facebook)
        self.register_blueprint(hc)
