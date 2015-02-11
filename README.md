# Flask AWS Scaffolding

add these entries to your hosts /etc/hosts file

127.0.0.1	app.dev auth.app.dev
127.0.0.1	es
127.0.0.1	mongo
127.0.0.1	influx

create virtualenv
pip install -r requirements.txt

to run app cd to base directory run `gunicorn -c /path/to/gunicorn.conf wsgi:app --reload`

see the nginx config file to setup nginx proxy and serve static resources
