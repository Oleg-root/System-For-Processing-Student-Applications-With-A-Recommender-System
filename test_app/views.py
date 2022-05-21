import pymorphy2
import pandas as pd
import datetime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from .models import Notification, Topic, StudentRequestForTopic, RequestResponse
from .forms import TopicForm, StudentRequestForTopicForm, RequestResponseForm, RequestResponseForm_student


def make_dataframe_from_topics():
    results = []
    for topic in Topic.objects.all():
        results.append({
            'topic_id': topic.id,
            'topic': topic.name_russian,
            'lecturer': topic.lecturer.last_name,
            'lecturer_interests': topic.lecturer.profile.interests,
            'important_features': ' '.join(process_query(topic.name_russian + ' ' + topic.lecturer.last_name + ' ' + topic.lecturer.profile.interests))
        })
    df = pd.DataFrame(data=results)
    df.to_csv(r'media/topic_db.csv', index=False)
    return df

def process_query(textQuery):
    morph = pymorphy2.MorphAnalyzer()
    cleanquery = []

    for word in textQuery.split():
        if len(word) > 3:
            cleanquery.append(morph.parse(word.replace(',', ''))[0].normal_form)

    return cleanquery

def make_recommendation(df, searchQuery):
    results = []
    new_row = df.iloc[-1, :].copy()
    query = process_query(searchQuery)
    new_row.iloc[-1] = " ".join(query)
    df = df.append(new_row)
    tfidVec = TfidfVectorizer().fit_transform(df["important_features"])
    cs = cosine_similarity(tfidVec, tfidVec)
    sim_scores = list(enumerate(cs[-1, :]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    for i in range(1, df.shape[0]):
        indx = sim_scores[i][0]
        if sim_scores[i][1] != 0.0:
            results.append([df["topic"].iloc[indx], df["topic_id"].iloc[indx]])

    return results

def search_venues(request):
    if request.method == "POST":
        if 'searched' in request.POST:
            searched = request.POST.get('searched')
            results = make_recommendation(pd.read_csv('media/topic_db.csv'), searched)
            topics = []

            for i in range(0, len(results)):
                topics.append(Topic.objects.get(id=results[i][1]))
        elif 'recommend' in request.POST:
            recommend = request.POST.get('recommend', '')
            results = make_recommendation(pd.read_csv('media/topic_db.csv'), recommend)
            topics = []

            for i in range(0, len(results)):
                topics.append(Topic.objects.get(id=results[i][1]))
            return render(request, 'test_app/search_venues.html', {'searched': recommend, 'topics': topics})

        elif 'searched_lecturers' and 'searched_interests' in request.POST:
            searched_lecturers = request.POST.get('searched_lecturers')
            searched_interests = request.POST.get('searched_interests')
            results = make_recommendation(pd.read_csv('media/topic_db.csv'), str(searched_lecturers) + ' ' + str(searched_interests))
            topics = []

            for i in range(0, len(results)):
                topics.append(Topic.objects.get(id=results[i][1]))

            return render(request, 'test_app/search_venues.html', {'searched_lecturers': searched_lecturers, 'searched_interests': searched_interests, 'topics': topics})

        return render(request, 'test_app/search_venues.html', {'searched': searched, 'topics': topics })
    else:
        return render(request, 'test_app/search_venues.html')


def create_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = Topic.objects.create(name_russian=form.cleaned_data.get('name_russian'),
                                         description=form.cleaned_data.get('description'),
                                         lecturer=request.user,
                                         date_created=datetime.datetime.now())
            topic.save()
            messages.success(request, f'Тема успешно добавлена!')
            return redirect('topics')
    else:
        if request.user.is_authenticated:
            form = TopicForm()
        else:
            messages.warning(request, f'Войдите в систему, чтобы просматривать данную страницу')
            return redirect('/login/?next=/topic/new/')

    return render(request, 'test_app/topic_create.html', {'form': form})

class TopicListView(ListView):
    model = Topic
    template_name = 'test_app/topics_with_base_filter.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'topics'
    ordering = ['-date_created']
    paginate_by = 7

class TopicDetailView(DetailView):
    model = Topic
    template_name = 'test_app/topic_detail.html'

class TopicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Topic
    template_name = 'test_app/topic_update.html'
    fields = ['name_russian', 'description']
    success_url = '/'

    def form_valid(self, form):
        form.instance.lecturer = self.request.user
        return super().form_valid(form)

    def test_func(self):
        topic = self.get_object()
        if self.request.user == topic.lecturer:
            return True
        else:
            return False

class TopicDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Topic
    success_url = '/'

    def test_func(self):
        topic = self.get_object()
        if self.request.user == topic.lecturer:
            return True
        else:
            return False

class UserTopicListView(ListView):
    model = Topic
    template_name = 'test_app/user_topics.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'topics'
    paginate_by = 3

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Topic.objects.filter(lecturer=user).order_by('-date_created')

def create_studentRequest(request, pk):
    if request.method == "POST":
        form = StudentRequestForTopicForm(request.POST)
        if form.is_valid():
            topic = Topic.objects.get(id=pk)
            studentRequest = StudentRequestForTopic.objects.create(student=request.user,
                                                                   receiver=topic.lecturer.username,
                                                                   associatedTopic=topic,
                                                                   description=form.cleaned_data.get('description'))
            studentRequest.save()
            messages.success(request, f'Заявка на тему успешно отправлена!')
            return redirect('topics')
    else:
        if request.user.is_authenticated:
            if request.user == Topic.objects.get(id=pk).lecturer:
                return redirect('topic')

            form = StudentRequestForTopicForm()
        else:
            messages.warning(request, f'Войдите в систему, чтобы просматривать данную страницу')
            return redirect('/login/?next=/create_request')
    return render(request, 'test_app/create_request.html', {'form': form})

def create_studentRequestNoTopic(request, pk):
    if request.method == "POST":
        form = StudentRequestForTopicForm(request.POST)
        if form.is_valid():
            topic = Topic.objects.get(id=pk)
            studentRequest = StudentRequestForTopic.objects.create(student=request.user,
                                                                   receiver=topic.lecturer.username,
                                                                   associatedTopic=topic,
                                                                   description=form.cleaned_data.get('description'))
            studentRequest.no_topic = True
            studentRequest.save()
            messages.success(request, f'Заявка на взаимодействие успешно отправлена!')
            return redirect('topics')
    else:
        if request.user.is_authenticated:
            if request.user == Topic.objects.get(id=pk).lecturer:
                return redirect('topic')

            form = StudentRequestForTopicForm()
        else:
            messages.warning(request, f'Войдите в систему, чтобы просматривать данную страницу')
            return redirect('/login/?next=/create_request')
    return render(request, 'test_app/create_request_no_topic.html', {'form': form})

class StudentRequestListView(LoginRequiredMixin, ListView):
    model = StudentRequestForTopic
    template_name = 'test_app/student_requests.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        return StudentRequestForTopic.objects.filter(receiver=self.request.user).order_by('date_created')

class StudentRequestListView2(LoginRequiredMixin, ListView):
    model = StudentRequestForTopic, RequestResponse
    template_name = 'test_app/requests_from_student.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        return StudentRequestForTopic.objects.filter(student=self.request.user).order_by('-date_created')

def create_requestResponse(request, pk):
    if request.method == "POST":
        form = RequestResponseForm(request.POST)
        if form.is_valid():
            s = StudentRequestForTopic.objects.get(id=pk)
            requestResponse = RequestResponse.objects.create(lecturer=request.user,
                                               receiver=s.student.username,
                                               associatedRequest=s,
                                               content=form.cleaned_data.get('content'))
            requestResponse.save()
            s.responded = True
            s.lecturer_answer = form.cleaned_data.get('content')
            s.save()
            messages.success(request, f'Ответ успешно отправлен!')
            return redirect('topics')
    else:
        if request.user.is_authenticated:
            if request.user == StudentRequestForTopic.objects.get(id=pk).student:
                return redirect('topics')

            form = RequestResponseForm()
        else:
            messages.warning(request, f'Войдите в систему, чтобы просматривать данную страницу.')

            return redirect('/login/?next=/request_response/')

    return render(request, 'test_app/request_response.html', {'form': form, 'StudentRequestForTopic': StudentRequestForTopic.objects.get(id=pk)})

def accept_studentRequest(request, pk):
    if request.method == "POST":
        s = StudentRequestForTopic.objects.get(id=pk)
        other_requests = StudentRequestForTopic.objects.filter(associatedTopic__name_russian=s.associatedTopic.name_russian, no_topic=False).exclude(id=pk)
        if other_requests:
            other_requests.declined = True
            for newrequest in other_requests:
                new = StudentRequestForTopic.objects.create(student=newrequest.student,
                                                            receiver=s.receiver,
                                                            associatedTopic=s.associatedTopic,
                                                            description='[' + s.associatedTopic.name_russian + ']' + ' - ' + newrequest.description,
                                                            no_topic=True)
                new.save()
            other_requests.delete()
        associated_topic = s.associatedTopic
        s.accepted = True
        associated_topic.is_taken = True
        associated_topic.student_who_took = s.student.last_name + ' ' + s.student.first_name + ' ' + s.student.profile.patronym
        associated_topic.save()
        s.save()
        messages.success(request, f'Заявка принята!')
        return redirect('/student_requests/')
    return render(request, 'test_app/request_confirm_accept.html', {'StudentRequestForTopic': StudentRequestForTopic.objects.get(id=pk)})

def respond_to_lecturer_response(request, pk):
    if request.method == "POST":
        form = RequestResponseForm_student(request.POST)
        if form.is_valid():
            s = StudentRequestForTopic.objects.get(id=pk)
            s.student_answer = form.cleaned_data.get('content')
            s.responded_by_student = True
            s.save()
            messages.success(request, f'Ответ успешно отправлен преподавателю!')
            return redirect('topics')
    else:
        if request.user.is_authenticated:
            if request.user != StudentRequestForTopic.objects.get(id=pk).student:
                return redirect('topics')

            form = RequestResponseForm_student()
        else:
            messages.warning(request, f'Войдите в систему, чтобы просматривать данную страницу.')

            return redirect('/login/?next=/student_response/')

    return render(request, 'test_app/student_response.html', {'form': form, 'StudentRequestForTopic': StudentRequestForTopic.objects.get(id=pk)})

def decline_studentRequest(request, pk):
    if request.method == "POST":
        s = StudentRequestForTopic.objects.get(id=pk)
        s.declined = True
        s.save()
        return redirect('/student_requests/')
    return render(request, 'test_app/request_confirm_decline.html', {'StudentRequestForTopic': StudentRequestForTopic.objects.get(id=pk)})

class StudentRequestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = StudentRequestForTopic
    success_url = '/requests/'
    template_name = 'test_app/request_confirm_delete.html'
    def test_func(self):
        r = self.get_object()
        if self.request.user.username == r.receiver:
            return True
        elif self.request.user.username == r.student.username:
            return True
        else:
            return False

class StudentRequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StudentRequestForTopic
    fields = ['description']
    template_name = 'test_app/request_update.html'
    success_url = '/requests/'

    def form_valid(self, form):
        form.instance.student = self.request.user
        return super().form_valid(form)

    def test_func(self):
        r = self.get_object()
        if self.request.user.username == r.receiver:
            return True
        elif self.request.user.username == r.student.username:
            return True
        else:
            return False

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'test_app/notifications.html'
    page_kwarg = 'test_app/base.html'
    context_object_name = 'notifications'
    paginate_by = 5

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-date_created')

class NotificationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Notification
    success_url = '/notifications/'


    def test_func(self):
        n = self.get_object()
        if self.request.user == n.receiver:
            return True
        else:
            return False
