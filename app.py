from flask import Flask, request, jsonify, g, copy_current_request_context
from flasgger import Swagger
from flasgger.utils import swag_from, validate, ValidationError
import sqlite3
import json
import gevent
import gevent.pywsgi

DATABASE = 'db/status.db'


def writeToFile(ticketID, content):
    with open("output/"+str(ticketID)+".json",'w') as f:
        f.write(json.dumps(content))


def readFromFile(ticketID):
    data = ""
    with open("output/"+str(ticketID)+".json") as f:
        data = json.load(f)
    return data


def execute_query(query):
    cur = get_db().execute(query)
    lastid = cur.lastrowid
    cur.close()
    get_db().commit()
    return lastid


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

app = Flask(__name__)
swagger = Swagger(app)  # you can pass config here Swagger(app, config={})


def validation_helper(data, swagger_object, swaggerfile):
    try:
        validate(data, swagger_object, swaggerfile, __file__)
    except ValidationError as e:
        return "Validation Error: %s" % e, 400


@app.route('/query_analyse_features', methods=['POST'])
@swag_from('swagger/query_get_features.yml')
def post_get_query():
    data = request.json
    val = validation_helper(data=data, swagger_object='FeatureRequest', swaggerfile='swagger/query_get_features.yml')
    if val is not None:
        return val

    id = execute_query("INSERT INTO status (progress) VALUES (0);")

    response = []
    execute_query("UPDATE status SET progress = 100 WHERE id = " + str(id) + ";")

    @copy_current_request_context
    def calculate_features():
        for feature in data['features']:
            response.append({"name": feature,
                             "value": 0})
        writeToFile(id, response)
        execute_query("UPDATE status SET progress = 100 WHERE id = "+str(id)+";")
    gevent.spawn(calculate_features)
    return jsonify({"id": id,
                    "url": '/get_features/'+str(id)})


@app.route('/get_features/<int:ticketID>', methods=['GET'])
@swag_from('swagger/get_feature.yml')
def get_features(ticketID):
    ticket = query_db('select * from status where id = ?;', [ticketID], one=True)
    if ticket is None:
        return 'No such ticket'
    else:
        progress = ticket[1]
        if progress == 100:
            return jsonify(readFromFile(ticketID))
        else:
            progress_text = 'Your progress: ' + str(progress) + "%. Please wait and try again."
            return progress_text

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    gevent_server = gevent.pywsgi.WSGIServer(('localhost', 5000), app)
    gevent_server.serve_forever()  # instead of flask_app.run()
    #app.run(debug=True)