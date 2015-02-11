from flask import Blueprint, Response, render_template
from flask.views import MethodView
from app import config
import logging

dashboard = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

class Index(MethodView):

    def get(self):
        return render_template("index.html")

dashboard.add_url_rule("/", view_func=Index.as_view('index'))
