from django.contrib import admin
from .models import Degree
from .models import DegreeRequirement
from .models import Course
from django.contrib import admin
from django.contrib.postgres import fields
from jsoneditor.forms import JSONEditor
from .models import Major
from .models import Minor
from .models import Specialisation
from django import forms
import json

# Register your models here.

class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = "__all__"

    def clean(self):
        level = self.cleaned_data.get('level')
        graduation = self.cleaned_data.get('graduation_stage')
        if (int(level) > 4000 and graduation == "Undergraduate"):
            raise forms.ValidationError("Cannot set a 5000-8000 level course to undergraduate")
        self.validate_is_list('majors')
        self.validate_is_list('minors')
        self.validate_is_list('incompatible')
        return self.cleaned_data
    def validate_is_list(self, identifier):
        arr = self.cleaned_data.get(identifier)
        if(arr == ""):
            return
        try:
            print(arr.replace("'","\""))
            json.loads(arr.replace("'","\""))
        except Exception as e:
            print(e)
            raise forms.ValidationError(identifier.upper()+" must be in list format")


class CourseAdmin(admin.ModelAdmin):
    form = CourseForm
    search_fields = ('name','code')
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditor},
    }




class DegreeRequirementAdmin(admin.ModelAdmin):
    search_fields = ('name','code')
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditor},
    }

class MajorAdmin(admin.ModelAdmin):
    search_fields = ('name','code')
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditor},
    }

class MinorAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code')
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditor},
    }


class SpecialisationAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code')
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditor},
    }



admin.site.register(Degree)
admin.site.register(DegreeRequirement,DegreeRequirementAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(Minor, MinorAdmin)
admin.site.register(Specialisation,SpecialisationAdmin)
# Register your models here.

