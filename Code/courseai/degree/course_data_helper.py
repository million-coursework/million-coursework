import json
import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch


es_conn = Elasticsearch([os.environ.get("ES_IP")])


def get_course_data(codes):
    global es_conn
    course_data = {}

    codes = json.loads(codes)

    for code in codes:
        q = MultiMatch(query=code, fields=['course_code^4'])
        s = Search(using=es_conn, index='courseupdated')
        response = s.query(q).execute()

        if not response['hits']['hits']:
            continue
        hit = response['hits']['hits'][0].to_dict()

        course_data[hit['_source']['course_code']] = {
            "course_code": hit['_source']['course_code'],
            "id": hit["_id"],
            "versions": hit['_source']['versions']
        }

    return course_data


def track_metrics(degree_plan):
    return


def get_all():
    global es_conn
    s = Search(using=es_conn, index='courses')
    count = s.count()
    result = s[0:count].execute()['hits']['hits']
    result = sorted(result, key=lambda x: int(x["_id"]))
    return result
