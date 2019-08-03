from django.template import loader
from degree.course_data_helper import es_conn
from . import mms, search

import json
from django.http import HttpResponse


def index(request):
    if 'query' not in request.GET:
        template = loader.get_template('static_pages/search.html')
        return HttpResponse(template.render({}, request))

    original_query = request.GET['query']
    filters = request.GET.get('filters', None)
    codes = None
    levels = None
    sessions = None
    level = None

    if filters is not None:
        filters = json.loads(filters)

        if 'codes' in filters and filters['codes']:
            codes = filters['codes']

        if 'levels' in filters and filters['levels']:
            levels = filters['levels']

        if 'sessions' in filters and filters['sessions']:
            sessions = filters['sessions']

        if 'level' in filters:
            level = filters['level']

    return search.execute_search(es_conn, original_query, request, codes=codes, levels=levels, semesters_offered=sessions, level=level)


def mms_request(request):
    try:
        code = request.GET['query']
        return mms.get_mms_data(es_conn, code)
    except KeyError:
        raise Exception("Malformed JSON as input. Expects a field called query.")


def all_majors(request):
    try:
        name = request.GET['query']
        level = request.GET['level'] if 'level' in request.GET else None
        return mms.mms_by_name(es_conn, name, 'majors', level=level)
    except KeyError:
        return mms.search_all(es_conn, "MAJ")


def all_minors(request):
    try:
        name = request.GET['query']
        level = request.GET['level'] if 'level' in request.GET else None
        return mms.mms_by_name(es_conn, name, 'minors', level=level)
    except KeyError:
        return mms.search_all(es_conn, "MIN")


def all_specs(request):
    try:
        name = request.GET['query']
        level = request.GET['level'] if 'level' in request.GET else None
        return mms.mms_by_name(es_conn, name, 'specialisations', level=level)
    except KeyError:
        return mms.search_all(es_conn, "SPEC")


def course_lists(request):
    query = request.GET['query']
    return mms.course_lists(es_conn, query)
