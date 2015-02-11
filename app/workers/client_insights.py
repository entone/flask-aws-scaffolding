from app.app import App
from app import config
from app import INFLUX
from capuchin.insights import INSIGHTS
from flask_oauth import OAuth
import urlparse
import logging
import time
import requests
import datetime
from slugify import slugify

date_format = "%Y-%m-%dT%H:%M:%S+0000"

class ClientInsights():

    def __init__(self, client):
        self.oauth = OAuth()
        self.client = client
        self.fb_app = self.oauth.remote_app(
            'facebook',
            base_url='https://graph.facebook.com/',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            consumer_key=config.FACEBOOK_APP_ID,
            consumer_secret=config.FACEBOOK_APP_SECRET,
        )
        self.fb_app.tokengetter(self.get_token)
        self.get_insights()

    def get_token(self):
        return (self.client.facebook_page.token, config.FACEBOOK_APP_SECRET)

    def write_data(self, data):
        for insight in data.get("data", []):
            name = insight.get("name")
            for event in insight.get("values"):
                tm = time.mktime(time.strptime(event.get("end_time"), date_format))

                val = event.get("value")
                if isinstance(val, dict):
                    for k,v in val.iteritems():
                        t = "{}.{}".format(name, slugify(k))
                        self.write_influx((tm, v, t))
                else:
                    self.write_influx((tm, val, name))

    def get_insights(self):
        id = self.client.facebook_page.id
        for i in INSIGHTS:
            res = self.fb_app.get(
                "/v2.2/{}/insights/{}".format(id, i),
                data={"period":"day"}
            )
            logging.info(res.data)
            self.write_data(res.data)
            self.page(res.data)

    def page(self, data):
        nex = data.get("paging", {}).get("previous")
        end_date = int(urlparse.parse_qs(urlparse.urlparse(nex).query)['until'][0])
        end_date = datetime.datetime.fromtimestamp(end_date)
        stop = end_date - datetime.timedelta(days=90)
        logging.info(end_date)
        last = nex
        while nex:
            res = requests.get(nex)
            data = res.json()
            logging.info(data)
            self.write_data(data)
            nex = data.get("paging", {}).get("previous")
            end_date = int(urlparse.parse_qs(urlparse.urlparse(nex).query)['until'][0])
            end_date = datetime.datetime.fromtimestamp(end_date)
            if end_date < stop or not data.get("data"): nex = None

        return True

    def write_influx(self, event):
        time, val, typ = event
        data = [
            dict(
                name = "insights.{}.{}".format(self.client._id, typ),
                columns = ["time", "value", "typ"],
                points = [[time, val, typ.split(".")[-1]]]
            )
        ]
        logging.info("Writing: {}".format(data))
        try:
            res = INFLUX.write_points(data)
            logging.info(res)
        except Exception as e:
            logging.warning(e)
