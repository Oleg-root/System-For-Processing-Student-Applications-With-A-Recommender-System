from django import forms
from .models import Topic, StudentRequestForTopic, RequestResponse



class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name_russian', 'description']

class StudentRequestForTopicForm(forms.ModelForm):
    class Meta:
        model = StudentRequestForTopic
        fields = ['description']

class RequestResponseForm(forms.ModelForm):
    class Meta:
        model = RequestResponse
        fields = ['content']

