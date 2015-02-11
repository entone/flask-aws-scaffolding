from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch import TransportError
from flaskaws import config
from flaskaws import user_mapping
from flaskaws import influx
import influxdb
import gevent
import logging

def init_elasticsearch():
    es_connected = False
    while not es_connected:
        try:
            ES = Elasticsearch(
                hosts=config.ES_HOSTS,
                sniff_on_start=True,
                sniff_on_connection_fail=True,
                sniffer_timeout=60
            )
            es_connected = True
            logging.info(ES)
        except TransportError as e:
            logging.info("Elasticsearch not connected")
            logging.error(e)
            gevent.sleep(1)
    return ES

def init_mongodb():
    mongo_connected = False
    while not mongo_connected:
        try:
            MONGO = MongoClient(config.MONGO_HOST, config.MONGO_PORT)
            mongo_connected = True
        except Exception as e:
            logging.info("MongoDB not connected")
            logging.error(e)
            gevent.sleep(1)

    return MONGO

def init_influxdb():
    logging.info("INFLUX")
    influx_connected = False
    while not influx_connected:
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
            logging.info("Influxdb not connected")
            logging.error(e)
            gevent.sleep(1)

    return INFLUX

def create_index(ES):
    exists = ES.indices.exists(config.ES_INDEX)
    logging.info("Exists: {}".format(exists))
    if not exists:
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
    return

def create_shards(INFLUX):
    logging.info("Creating Influxdb shards and continuous queries")
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
    except Exception as e:
        logging.error(e)
