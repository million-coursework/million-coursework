from django.http import HttpResponse
from django.template import loader


def planner(request):
    template = loader.get_template('dynamic_pages/planner.html')
    user = None
    if not request.user is None:
        user = request.user

    context = {
        'degree_name': request.GET['degreeName'],
        'degree_code': request.GET['degreeCode'],
        'start_year': request.GET['startyear'],
        'start_sem': request.GET['semester'],
        'user': user
    }

    for key, name in [('saveCode', 'save_code'),
                      ('degreeName2', 'degree_name2'),
                      ('degreeCode2', 'degree_code2')]:
        if key in request.GET:
            context[name] = request.GET[key]

    return HttpResponse(template.render(context))
