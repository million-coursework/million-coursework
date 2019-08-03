from django.http import JsonResponse

from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch


def area_filter(areas):
    """
    :param areas: The course areas to search by (eg. ["COMP", "MATH"])
    :return: A query object that searches at least one of the areas
    :raise: AssertionError if areas is None
    """

    if areas is None:
        raise AssertionError("Argument to areas must not be None")

    area_filters = []

    if len(areas) == 1:
        return Q('match', area=areas[0])

    for area in areas:
        area_filters.append(Q('match', area=area))

    return Q('bool', should=area_filters, minimum_should_match=1)


def level_filter(levels):
    if levels is None:
        raise AssertionError("Argument to areas must not be None")

    if len(levels) == 1:       # Add an extra level filter to avoid a bug which comes up
        levels.append("10000")  # when there is exactly 1 level filter and 1 code filter

    level_filters = []

    for level in levels:
        level_filters.append(Q('match', level=level))

    return Q('bool', should=level_filters, minimum_should_match=1)


def get_levels(level):
    if level is None:
        return [str(i) for i in range(1000, 10000, 1000)]
    if level.lower() == 'undergraduate':
        return [str(i) for i in range(1000, 6000, 1000)]
    if level.lower() == 'postgraduate':
        return [str(i) for i in range(6000, 10000, 1000)]
    return []


def raw_search(search_object, phrase, areas, levels, sem_queried, level):
    should = []

    fields = []

    for field in range(2014, 2020):
        # fields.append('versions.' + str(field) + '.title^3')
        fields.append('versions.' + str(field) + '.prescribed_texts^2')
        fields.append('versions.' + str(field) + '.description^1.5')
        fields.append('versions.' + str(field) + '.learning_outcomes')
        fields.append('versions.' + str(field) + '.convener')

    for word in phrase.split():
        should.append(MultiMatch(query=word, fields=fields))

    fields2 = ['course_code^4']

    for field in range(2014, 2020):
        fields2.append('versions.' + str(field) + '.title^3')

    for word in phrase.split():
        should.append(MultiMatch(type='phrase_prefix', query=word, fields=fields2))

    q = Q('bool', should=should, minimum_should_match=1)
    response = search_object.query(q)

    if areas is not None:
        q2 = area_filter(areas)
        response = response.query(q2)

    if levels is not None:
        q2 = level_filter(levels)
        response = response.query(q2)

    elif levels is None and areas is not None:
        #  Not sure why this clause is required. I'll get back to it when I have more time

        # if levels is None, create a "fake" levels query
        q2 = level_filter(get_levels(level))
        response = response.query(q2)

    if level is not None:
        if len(level) > 2:
            level = level[0].upper() + level[1:].lower()
        if level not in ['Undergraduate', 'Postgraduate']:
            print('Level not recognised: ' + level)
        q2 = Q('match', ugpg=level)
        response = response.query(q2)

    count = response.count()
    response = response[0:count].execute()

    course_list = []
    for hit in response['hits']['hits']:

        hit = hit.to_dict()

        if sem_queried is None:
            course_list.append(hit['_source'])
            continue

        for sem in sem_queried:
            try:
                sem_offered = hit['_source']['versions'][str(sem['year'])]['sessions']

                if sem['semester'] in sem_offered:
                    course_list.append(hit['_source'])
                    break

            except KeyError:
                continue
    return course_list


def __filtered_search(search_object, phrase, filter_string, codes, levels, sem_queried=None, level=None):
    q2 = Q('bool',
           should=[Q('match_phrase', title=filter_string),
                   Q('match_phrase', code=filter_string),
                   Q('match_phrase', description=filter_string),
                   Q('match_phrase', outcome=filter_string)],
           minimum_should_match=1
           )

    should = []
    for word in phrase.split(" "):
        should.append(
            MultiMatch(query=word, type="phrase_prefix", fields=['code^4', 'title^3', 'description^1.5', 'outcome']))
    q = Q('bool', should=should, minimum_should_match=1)

    if codes is None and levels is None:
        response = search_object.query(q).query(q2)
        count = response.count()
        response = response[0:count].execute()

    elif codes is None and levels is not None:
        q3 = level_filter(levels)
        response = search_object.query(q).query(q2).query(q3)
        count = response.count()
        response = response[0:count].execute()

    elif codes is not None and levels is None:
        q4 = area_filter(codes)
        response = search_object.query(q).query(q2).query(q4)
        count = response.count()
        response = response[0:count].execute()

    else:  # both are not none
        q4 = area_filter(codes)
        q3 = level_filter(levels)
        response = search_object.query(q).query(q2).query(q3).query(q4)
        count = response.count()
        response = response[0:count].execute()

    course_list = []
    for hit in response['hits']['hits']:
        # perform the semester filtering here
        sem_offered = hit['_source']['semester']
        if sem_queried is None:
            course = {'code': hit['_source']['code'], 'title': hit['_source']['title']}

        elif len(sem_queried) == 2 and len(sem_offered) != 0:
            course = {'code': hit['_source']['code'], 'title': hit['_source']['title']}

        elif len(sem_queried) == 1 and sem_queried[0] == 1 and (1 in sem_offered):
            course = {'code': hit['_source']['code'], 'title': hit['_source']['title']}

        elif len(sem_queried) == 1 and sem_queried[0] == 2 and (2 in sem_offered):
            course = {'code': hit['_source']['code'], 'title': hit['_source']['title']}

        else:
            continue
        course_list.append(course)

    return course_list


def course_search(search_object, phrase):
    # this search object should use the index called degrees
    q = Q('regexp', name="*" + phrase + "*")
    response = search_object.query(q).execute()

    degree_list = [(hit['_source']['name'] for hit in response['hits']['hits'])]

    return degree_list


# need a way to initiate Elastic instance only once

def execute_search(es_conn, phrase, request, codes, levels, semesters_offered=None, level=None):
    s = Search(using=es_conn, index='courseupdated')

    # if '\"' in phrase:
    #     c = '\"'
    #
    #     quote_positions = [pos for pos, char in enumerate(phrase) if char == c][:2]
    #     if len(quote_positions) < 2 or quote_positions[1] - quote_positions[0] < 2:
    #         response = raw_search(s, phrase, codes, levels, sem_queried=semesters_offered, level=level)
    #
    #     else:
    #         f_string = phrase[quote_positions[0] + 1: quote_positions[1]]
    #         response = __filtered_search(s, phrase, f_string, codes, levels, sem_queried=semesters_offered, level=level)
    # 
    # else:
    response = raw_search(s, phrase, codes, levels, sem_queried=semesters_offered, level=level)

    resp = {'query': phrase, 'response': response}
    return JsonResponse(resp)
