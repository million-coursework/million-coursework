from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile

class ProfileInline(admin.StackedInline):    # avoid displaying Profiles in plural
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    # add profile fields to list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_location', 'is_staff')
    list_select_related = ('profile', )

    def get_location(self, instance):
        return instance.profile.degree_plan_code
    get_location.short_description = 'degree plan code'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
