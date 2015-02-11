from flask import Flask, redirect, url_for, request
from flask_pjax import PJAX
from flask.ext.login import LoginManager, current_user
from flask.ext.session import Session
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch import TransportError
from models.client import Admin
import influx
import user_mapping
from slugify import slugify
from gevent import monkey
import influxdb
import humongolus
import config
import logging
import time
import gevent

monkey.patch_all()

logging.basicConfig(level=config.LOG_LEVEL)
es_connected = False

while not es_connected:
    try:
        gevent.sleep(1)
        logging.info("Elasticsearch not connected")
        ES = Elasticsearch(
            hosts=config.ES_HOSTS,
            sniff_on_start=True,
            sniff_on_connection_fail=True,
            sniffer_timeout=60
        )
        es_connected = True
    except TransportError as e:
        logging.error(e)

try:
    MONGO = MongoClient(config.MONGO_HOST, config.MONGO_PORT)
except Exception as e:
    logging.error(e)

influx_connected = False
while not influx_connected:
    gevent.sleep(1)
    logging.info("Influxdb not connected")
    INFLUX = influxdb.InfluxDBClient(
        config.INFLUX_HOST,
        config.INFLUX_PORT,
        config.INFLUX_USER,
        config.INFLUX_PASSWORD,
        config.INFLUX_DATABASE,
    )
    try:
        res = INFLUX.request("cluster_admins")
        influx_connected = True
    except Exception as e:
        logging.error(e)

logging.info("Databases UP")

def create_index():
    ES.indices.create(
        index=config.ES_INDEX,
        body = {
            "settings":user_mapping.SETTINGS,
            "mappings":{
                "user":{
                    "_source":{"enabled":True},
                    "properties":user_mapping.USER
                }
            }
        }
    )

class App(Flask):

    def __init__(self):
        super(App, self).__init__("app")
        self.config.from_object('app.config')
        logging.info("SERVER_NAME: {}".format(self.config['SERVER_NAME']))
        if not ES.indices.exists(config.ES_INDEX):
            create_index()
        humongolus.settings(logging, MONGO)
        logging.info("Initialized")
        try:
            self.init_influx()
            self.init_session()
            self.init_login()
            self.init_blueprints()
            self.init_pjax()
            self.init_templates()
        except Exception as e:
            logging.exception(e)

        logging.info("Running")

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

    def init_session(self):
        self.config['SESSION_MONGODB'] = MONGO
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

    def init_influx(self):
        data = {
            "name":config.INFLUX_DATABASE,
            "spaces":influx.SPACES,
            "continuousQueries":influx.QUERIES,
        }
        try:
            res = INFLUX.request(
                url="cluster/database_configs/{}".format(config.INFLUX_DATABASE),
                data=data,
                method="POST"
            )
            logging.debug(res)
        except Exception as e:

            logging.warning(e)


    def init_blueprints(self):
        from controllers.dashboard import dashboard
        from controllers.auth import auth
        from controllers.auth.facebook import facebook
        dashboard.before_request(self.user_logged_in)
        self.register_blueprint(dashboard)
        self.register_blueprint(auth)
        self.register_blueprint(facebook)
