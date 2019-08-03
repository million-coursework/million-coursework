import os
import json
import django
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch

def set_up_degree_requirements_db():
    # adds json object to db
    def add_to_db(data):
        year = data["year"]
        code = data["code"]
        name = data["name"]
        required = data["required"]
        units = data["units"]
        dr = DegreeRequirement(year=year, code=code, name=name, required=required, units=units)
        dr.save()

    from degree.models import DegreeRequirement

    for filename in os.listdir("static/json/"):
        try:
            with open('static/json/{}'.format(filename)) as file:
                add_to_db(json.loads(file.read()))
        except:
            pass

def sync_course_db():
    es_conn = Elasticsearch([os.environ.get("ES_IP")])

    res = es_conn.search(size=10000)

    results = []
    scroll_size = res['hits']['total']

    print(scroll_size)

    from degree.models import Course
    while (scroll_size > 0):
        try:
            results += res['hits']['hits']
            scroll_id = res['_scroll_id']
            res = es_conn.scroll(scroll_id=scroll_id, scroll='60s')
            scroll_size = len(res['hits']['hits'])
        except:
            break

    for result in results:
        print("saved")
        res_dict = result["_source"]
        course = Course(name = res_dict['name'],
                        code = res_dict['code'],
                        semesters = res_dict['semester'],
                        prerequisite_text=res_dict['prereq_text'],
                        title = res_dict['title'],
                        level= res_dict['level'],
                        area= res_dict['area'],
                        prerequisite_cnf = res_dict['pre_req_cnf'],
                        description = res_dict['description'],
                        outcome = res_dict['outcome'])
        course.save(no_es=True)



if __name__ == "__main__":
    print("seting up")
    django.setup()
    set_up_degree_requirements_db()
    sync_course_db()

