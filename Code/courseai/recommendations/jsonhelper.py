import json


def parse_degree_json(json_obj):
    json_deg = json.loads(json_obj)
    if 'courses' in json_deg:
        courses = json_deg['courses']
    else:
        courses = json_deg
    result = []
    for sem in courses:
        for s in sem:
            for course in sem[s]:
                if course['code'] == "Elective Course":
                    continue
                result.append(course['code'])
    return result
