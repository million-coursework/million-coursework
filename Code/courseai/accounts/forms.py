from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

User = get_user_model() # needed for user registration

class UserLoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)    # hidden passwords are not stored in plain text

    # when form is doing validation, "form.is_valid()",
    # check email, password, whether user is registered, whether user is active.
    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user_qs = User.objects.filter(username=email)
        if user_qs.count() == 0:
            raise forms.ValidationError("The user does not exist")
        else:
            if email and password:
                user = authenticate(username=email, password=password)
                if not user:
                    raise forms.ValidationError("Incorrect password")
                if not user.is_active:
                    raise forms.ValidationError("This user is no longer active")
        return super(UserLoginForm, self).clean(*args, **kwargs)    # return default, not giving field error.


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    username = forms.EmailField(label="Email address")  # override default email
    username2 = forms.EmailField(label="Confirm email")
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta():    # information about class
        model = User
        fields = [    # order matters
            'username',
            'username2',
            'password',
            'password2'
        ]

    def clean_username2(self):    # method name needs to contain field name
        """ Same as 'clean' method but give field error. """
        username = self.cleaned_data.get("username")
        username2 = self.cleaned_data.get("username2")
        if username != username2:
            raise forms.ValidationError("Emails must match")

        email_db = User.objects.filter(email = username)
        if email_db.exists():
            raise forms.ValidationError("This email has already been registered")
        return username

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            self.add_error('password2', "Password does not match")
        if len(password) < 6:
            raise forms.ValidationError('The password must contain at least six characters.')
        return password
