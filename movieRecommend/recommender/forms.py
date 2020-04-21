from django import forms
from django.contrib.auth.models import User
from recommender.models import Profile

class SearchBar(forms.Form):
    search = forms.CharField()

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username','password','email')

class UserProfileInfoForm(forms.ModelForm):
    class Meta():
        model = Profile
        fields = ('profile_pic','fav_actor')