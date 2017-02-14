from flask import copy_current_request_context, jsonify
from werkzeug.local import LocalProxy

from app import get_db
from util import FileWriter, orm

import gevent


def post(request):
    status = orm.Status()
    status.progress = 100

    db = LocalProxy(get_db)

    db.add(status)
    db.commit()

    ticket_id = status.id

    @copy_current_request_context
    def calculate_features():
        response = []
        for feature in request['features']:
            response.append({"name": feature,
                             "value": 0})
        FileWriter.write_to_file(ticket_id, response)

    gevent.spawn(calculate_features)
    return ticket_id


def get(ticket_id):
    db = LocalProxy(get_db)
    status = db.query(orm.Status).filter(orm.Status.id == ticket_id).one_or_none()

    if status is None:
        return 'Not found', 404

    elif status.progress < 100:
        return 'Request is processing ... Progress : {0} %'.format(str(status.progress))

    else:
        return jsonify(FileWriter.read_from_file(ticket_id))
