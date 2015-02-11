from werkzeug.wsgi import peek_path_info
from flaskaws import config
from flaskaws.app import App
import logging

def create_app():
    logging.basicConfig(level=config.LOG_LEVEL)
    logging.info("Initializing")
    _app = App()
    _app.configure_dbs()
    def app(env, start_response):
        if peek_path_info(env) == "healthcheck":
            _app.config['SERVER_NAME'] = None
        else:
            _app.config['SERVER_NAME'] = config.SERVER_NAME

        return _app(env, start_response)

    logging.info("Running")
    return app

app = create_app()
