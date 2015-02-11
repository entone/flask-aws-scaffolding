from flask import Blueprint, Response
from flask.views import MethodView
import logging

hc = Blueprint(
    'healthcheck',
    __name__,
)

class HealthCheck(MethodView):

    def get(self):
        logging.info("healthcheck!")
        return Response()

hc.add_url_rule("/healthcheck", view_func=HealthCheck.as_view('healthcheck'))
