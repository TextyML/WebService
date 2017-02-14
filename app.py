import logging
import connexion
import gevent.pywsgi
from connexion import RestyResolver
# Global context
from flask import g
#Database
from util import orm

logging.basicConfig(level=logging.INFO)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = orm.init_db('sqlite:///db')
    return db

app = connexion.App(__name__)
application = app.app


@application.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.remove()

if __name__ == '__main__':
    app.add_api('apiSpec.yaml', arguments={'title': 'RestyResolver Example'}, resolver=RestyResolver('api'))
    gevent_server = gevent.pywsgi.WSGIServer(('localhost', 8080), app)
    gevent_server.serve_forever()