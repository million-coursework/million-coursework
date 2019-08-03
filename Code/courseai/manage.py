#!/usr/bin/env python
import os
import sys

def sync_db():

    import django
    django.setup()

    from degree.models import DegreeRequirement, Major, Course, Minor, Specialisation
    from degree.sync import set_up_degree_requirements_db, sync_major_db, sync_course_db, sync_minor_db, sync_spec_db

    # clean db
    print("Cleaning db...")
    DegreeRequirement.objects.all().delete()
    Major.objects.all().delete()
    Course.objects.all().delete()
    Minor.objects.all().delete()
    Specialisation.objects.all().delete()

    # sync db
    print("Initialising requirements...")
    set_up_degree_requirements_db()
    print("Syncing majors with Elastic Search...")
    sync_major_db()
    print("Syncing courses with Elastic Search...")
    sync_course_db()
    print("Syncing minors with Elastic Search...")
    sync_minor_db()
    print("Syncing specialisations with Elastic Search...")
    sync_spec_db()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "courseai.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if(sys.argv[1] == 'syncdb'):
        sync_db()
    else:
        execute_from_command_line(sys.argv)

