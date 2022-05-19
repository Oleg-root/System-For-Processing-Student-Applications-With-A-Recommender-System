from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

WHOAMI_CHOICES = [
    ('student', 'Я студент'),
    ('lecturer', 'Я преподаватель')
]

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=100, label='Ваша электронная почта', required=True)
    first_name = forms.CharField(max_length=100, label='Ваше Имя', required=True)
    last_name = forms.CharField(max_length=100, label='Ваша Фамилия', required=True)
    patronym = forms.CharField(max_length=100, label='Ваше Отчество')
    student_or_lecturer = forms.ChoiceField(label='Кем вы являетесь?', choices=WHOAMI_CHOICES ,widget=forms.RadioSelect, required=True)

    class Meta: # Gives us nested namespace for configurations and keeps the configurations in one space
        model = User # model that will be affected (form.save() - save it to the User model)
        #fields = ['first_name', 'last_name', 'patronym', 'student_or_lecturer', 'username', 'email', 'password1', 'password2']
        fields = ['last_name', 'first_name', 'patronym', 'student_or_lecturer', 'username', 'email', 'password1',
                  'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['interests', 'image']
