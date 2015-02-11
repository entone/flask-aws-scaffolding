from app.app import INFLUX
import logging

class Event(object):

    def __init__(self, client, event, **kwargs):
        super(Event, self).__init__()
        columns = ["type"]
        values = [event]
        for k,v in kwargs.iteritems():
            columns.append(k)
            values.append(v)
        data = [
            dict(
                name = "events.{}.{}".format(client._id, event),
                columns = columns,
                points = [values]
            )
        ]
        logging.info("Writing: {}".format(data))
        try:
            res = INFLUX.write_points(data)
            logging.info(res)
        except Exception as e:
            logging.warning(e)
