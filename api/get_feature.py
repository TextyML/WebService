from flask import copy_current_request_context, jsonify
from werkzeug.local import LocalProxy
import json

from app import get_db
from util import FileWriter, orm

import gevent

from textyml import Preprocessor, LinguisticVectorizer
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


def post(request):
    status = orm.Status()
    status.progress = 0

    db = LocalProxy(get_db)

    db.add(status)
    db.commit()

    ticket_id = status.id

    @copy_current_request_context
    def calculate_features():
        response = []

        preprocessor = Preprocessor(stopwords=stopwords.words('english'),
                                    stemmer=SnowballStemmer("english"))

        lv = LinguisticVectorizer()

        documents = []

        for text in request:
            documents.append(preprocessor.get_preprocessed_text(text))

        features = list(lv.transform(documents).flatten())
        feature_names = lv.get_feature_names()

        for i in range(0, int(len(features) / len(feature_names))):
            print(i)
            document_result = []
            for x, feature in enumerate(features[i*len(feature_names):i*len(feature_names)+len(feature_names)]):
                document_result.append({"name": feature_names[x],
                                 "value": feature})
            response.append(document_result)
        new_status = db.query(orm.Status).filter(orm.Status.id == ticket_id).one_or_none()
        new_status.progress = 100
        new_status.result = json.dumps(response)
        db.commit()

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
        return jsonify(json.loads(status.result))
