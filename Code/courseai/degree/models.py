from django.db import models
import json
from degree.course_data_helper import es_conn
from django.forms import ValidationError
from django.contrib.postgres.fields import JSONField


# Create your models here.
class Degree(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=150)
    requirements = models.TextField()
    number_of_enrolments = models.IntegerField(default=1)
    metrics = models.TextField(default="{}")

    def __str__(self):
        return self.name


class PreviousStudentDegree(models.Model):
    code = models.CharField(max_length=10)
    courses_taken = models.TextField()

class DegreePlanStore(models.Model):
    """
        Stores plaintext for plan
    """
    code = models.CharField(max_length=10)
    plan = models.TextField()

class Major(models.Model):

    es_id = models.CharField(max_length=10, editable=False, default="")
    name = models.TextField(default="", blank=True)
    code = models.CharField(max_length=9, default="", blank=True)
    year = models.CharField(max_length=4, default="", blank=True, editable=False)
    description = models.TextField(default="", blank=True)
    graduation_stage = models.CharField(max_length=60, default="undergraduate",
                                    choices=(("undergraduate", "undergraduate"), ("postgraduate", "postgraduate")))
    requirements = JSONField(default=list)
    learning_outcomes = models.TextField(default="", blank=True)


    def _es_body(self):
        data = Major.objects.filter(code=self.code)

        initial = data[0]
        source = {}
        source['level'] = initial.graduation_stage
        source['code'] = initial.code

        versions = {}
        for major_model in data:
            version = {}

            version['requirements'] = major_model.requirements
            version['description'] = major_model.description
            version['title'] = major_model.name
            version['learning_outcomes'] = major_model.learning_outcomes
            versions[major_model.year] = version

        source['versions'] = versions
        return source

    def save(self,no_es=False):
        #self.validate_plan()
        super().save()
        if(no_es):
            return
        r = es_conn.update(index='majors', doc_type='_doc', id=self.es_id, refresh=True, body={"doc":self._es_body()})
        print(r)

    def __str__(self):
        return self.code + " - " + self.name + " " + self.year

class Minor(models.Model):

    es_id = models.CharField(max_length=10, editable=False, default="")
    name = models.TextField(default="", blank=True)
    code = models.CharField(max_length=9, default="", blank=True)
    year = models.CharField(max_length=4, default="", blank=True, editable=False)
    description = models.TextField(default="", blank=True)
    graduation_stage = models.CharField(max_length=60, default="undergraduate",
                                    choices=(("undergraduate", "undergraduate"), ("postgraduate", "postgraduate")))
    requirements = JSONField(default=list)
    learning_outcomes = models.TextField(default="", blank=True)


    def _es_body(self):
        data = Minor.objects.filter(code=self.code)

        initial = data[0]
        source = {}
        source['level'] = initial.graduation_stage
        source['code'] = initial.code

        versions = {}
        for minor_model in data:
            version = {}

            version['requirements'] = minor_model.requirements
            version['description'] = minor_model.description
            version['title'] = minor_model.name
            version['learning_outcomes'] = minor_model.learning_outcomes
            versions[minor_model.year] = version

        source['versions'] = versions
        return source

    def save(self,no_es=False):
        #self.validate_plan()
        super().save()
        if(no_es):
            return
        r = es_conn.update(index='minors', doc_type='_doc', id=self.es_id, refresh=True, body={"doc":self._es_body()})
        print(r)

    def __str__(self):
        return self.code + " - " + self.name + " " + self.year


class Specialisation(models.Model):

    es_id = models.CharField(max_length=10, editable=False, default="")
    name = models.TextField(default="", blank=True)
    code = models.CharField(max_length=9, default="", blank=True)
    year = models.CharField(max_length=4, default="", blank=True, editable=False)
    description = models.TextField(default="", blank=True)
    graduation_stage = models.CharField(max_length=60, default="undergraduate",
                                    choices=(("undergraduate", "undergraduate"), ("postgraduate", "postgraduate")))
    requirements = JSONField(default=list)
    learning_outcomes = models.TextField(default="", blank=True)


    def _es_body(self):
        data = Specialisation.objects.filter(code=self.code)

        initial = data[0]
        source = {}
        source['level'] = initial.graduation_stage
        source['code'] = initial.code

        versions = {}
        for spec_model in data:
            version = {}

            version['requirements'] = spec_model.requirements
            version['description'] = spec_model.description
            version['title'] = spec_model.name
            version['learning_outcomes'] = spec_model.learning_outcomes
            versions[spec_model.year] = version

        source['versions'] = versions
        return source

    def save(self,no_es=False):
        #self.validate_plan()
        super().save()
        if(no_es):
            return
        r = es_conn.update(index='minors', doc_type='_doc', id=self.es_id, refresh=True, body={"doc":self._es_body()})
        print(r)

    def __str__(self):
        return self.code + " - " + self.name + " " + self.year

class Course(models.Model):
    es_id = models.CharField(max_length=10, editable=False, default=0)
    creation_id = 0
    name = models.TextField(default="",blank=True)
    code = models.CharField(max_length=9,default="",blank=True)
    semesters = models.TextField(default="",blank=True)
    prerequisite_text=models.TextField(default="",blank=True)
    prerequisites = models.TextField(default="",blank=True)
    incompatible = models.TextField(default="",blank=True)
    min_units = models.CharField(max_length=5,blank=True)
    level = models.CharField(max_length=4,default=1000,blank=True)
    area = models.CharField(max_length=4,default="",blank=True)
    description=models.TextField(default="",blank=True)
    graduation_stage = models.CharField(max_length=60,default="Undergraduate", choices=(("Undergraduate","Undergraduate"),("Postgraduate","Postgraduate")))
    convenor = models.TextField(default="",blank=True)
    units = models.CharField(max_length=60, default="",blank=True)
    year = models.CharField(max_length=4,default=2018,blank=True)
    minors = models.TextField(default="",blank=True)
    majors = models.TextField(default="",blank=True)
    learning_outcomes = models.TextField(default="",blank=True)

    # generate the es body including version, will develop this outside pycharm
    def _es_body(self):
        data = Course.objects.filter(code=self.code)

        initial = data[0]
        source = {}
        source['level'] = initial.level
        source['area'] = initial.area
        source['course_code'] = initial.code
        source['ugpg'] = initial.graduation_stage

        versions = {}
        for course_model in data:
            version = {}
            prereq_incompatible = {"pre-requisite": course_model.prerequisites,"incompatible":course_model.incompatible, "min-units":course_model.min_units}

            semesters = course_model.semesters
            if not (course_model.semesters == ""):
                semesters = json.loads(course_model.semesters.replace("'", "\""))

            version['prerequisite_text'] = course_model.prerequisite_text
            version['prerequisites'] = prereq_incompatible
            version['sessions'] = semesters
            version['units'] = course_model.units
            version['description'] = course_model.description
            version['title'] = course_model.name
            version['convener'] = course_model.convenor
            version['majors'] = course_model.majors
            version['minors'] = course_model.minors
            version['learning_outcomes'] = course_model.learning_outcomes

            versions[course_model.year] = version

        source['versions'] = versions
        return source

    def __str__(self):
        return self.code+" - "+self.name+" "+self.year

    def save(self,no_es=False):
        super().save()
        self.creation_id+=1
        if(no_es):
            return
        if(self.es_id == ""):
            es_conn.create(index='courseupdated', doc_type='_doc',id = self.creation_id,
                               body={"doc": self._es_body()})
            return
        r = es_conn.update(index='courseupdated', doc_type='_doc', id=self.es_id, refresh=True, body={"doc":self._es_body()})
        print(r)

    def delete(self):
        to_update = self._es_body()
        to_update["versions"].pop(self.year)
        es_conn.update(index='courseupdated', doc_type='_doc', id=self.es_id, refresh = True,body={"doc":to_update})
        super().delete()

class DegreeRequirement(models.Model):
    year = models.CharField(max_length=4, default="")
    code = models.CharField(max_length=10,default="")
    name = models.TextField(default="",blank=True, editable=False)
    units = models.CharField(max_length=10,default="")
    required=JSONField(default=list)

    def __str__(self):
        return self.name+" - "+self.year

    def _json(self):
        to_return = {}
        to_return["year"] =self.year
        to_return["code"] = self.code
        to_return["name"] = self.name
        to_return["units"] = self.units
        to_return["required"] = self.required
        return json.dumps(to_return)


