from degree.models import Degree

from degree import course_data_helper
from recommendations.nn import get_prediction
from django.http import JsonResponse
from recommendations.jsonhelper import parse_degree_json
from .recommendations import get_recommendations

# Create your views here.


def recommend_course(request):
    plan = eval(request.GET['courses'])
    code = request.GET['code']

    course_list = parse_degree_json(request.GET['courses'])

    if code == 'NDSTE':
        if 'ENGN6626' in course_list:
            les_recommendations = ['ENGN6516', 'COMP6780', 'ENGN6223', 'ENGN6627', 'COMP6240', 'ENGN8180', 'ENGN6334', 'ENGN6410', 'ENGN8535', 'COMP6730', 'ENGN6613', 'ENGN6520', 'ENGN6420', 'ENGN8602', 'BUSI7019', 'SCOM8015', 'COMP8400', 'ENGN6521', 'EMET7001', 'MGMT7030', 'EMET6007', 'MGMT7170', 'ENVS6202', 'MGMT8005', 'ENGN6512', 'COMP6340', 'COMP8620', 'COMP7240', 'STAT7055', 'ENGN2228']
        else:
            les_recommendations = ['ENGN6626', 'ENGN6516', 'ENGN6223', 'COMP6780', 'ENGN6627', 'COMP6240', 'ENGN8180', 'ENGN6334', 'ENGN6410', 'ENGN8535', 'COMP6730', 'ENGN6613', 'ENGN6520', 'ENGN6420', 'ENGN8602', 'SCOM8015', 'BUSI7019', 'COMP8400', 'ENGN6521', 'MGMT7030', 'EMET6007', 'ENGN6601', 'ENGN6512', 'COMP7240', 'ENVS6202', 'EMET7001', 'COMP6340', 'COMP8620', 'ENGN2228', 'SCOM6501']

        return_stuff = []
        for course in les_recommendations[:10]:
            if course in course_list:
                continue
            return_stuff.append({'course': course, 'reasoning': 'Other students with your electives also chose this course'})
        return JsonResponse({'response': return_stuff})

    algo_recommended = get_recommendations(course_list)
    d = Degree(code=code, requirements=str(plan))

    try:
        predictions, prediction_ratings = get_prediction(d, 20)
    except:
        to_return = []
        for course in algo_recommended:
            if course in course_list:
                continue
            degree = Degree.objects.filter(code=code)[0]
            if int(degree.number_of_enrolments) > 0:
                proportion = int(eval(degree.metrics)[course]) * 100 / int(degree.number_of_enrolments)
            else:
                proportion = 0
            to_return.append(
                {"course": course, "reasoning": '%.2f%% of students in your degree chose this course' % proportion})
        return JsonResponse({"response": to_return})

    to_return = []

    response = course_data_helper.get_all()

    for i in range(len(predictions)):

        course = predictions[i]
        course_rating = prediction_ratings[i]

        course -= 1
        course_code = response[course]["_source"]['code']
        student_has_already_completed_course = course_code in course_list
        if student_has_already_completed_course:
            continue

        if course_rating < 1:
            continue

        degree = Degree.objects.filter(code=code)[0]
        if int(degree.number_of_enrolments) > 0:
            proportion = int(eval(degree.metrics)[course_code]) * 100 / int(degree.number_of_enrolments)
        else:
            proportion = 0
        course_list.append(course_code)
        to_return.append(
            {"course": course_code, "reasoning": '%.2f%% of students in your degree chose this course.' % proportion})

    for course in algo_recommended:
        if course in course_list:
            continue

        to_return.append(
            {"course": course, "reasoning": 'You have taken similar courses.'})
    return JsonResponse({"response": to_return})
