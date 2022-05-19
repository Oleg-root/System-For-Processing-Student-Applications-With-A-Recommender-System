import datetime
import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from test_app.models import Topic
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}
session = requests.session()
now = datetime.datetime.now()

def load_data(year, page, session):
    url = 'https://www.hse.ru/edu/vkr/?faculty=135303&year=%d&page=%d' % (year, page)
    response = session.get(url, headers=headers)
    return response.text

def execute():
    year = 2020
    page = 1
    while True:
        data = load_data(year, page, session)
        soup = BeautifulSoup(data, 'html.parser')
        topics_list = soup.find('ul', {'class': 'vkr-list'})
        if topics_list is not None:
            for element in soup.find_all('li', {'class': 'vkr-card vkr-list__item'}):
                try:
                    topic_name = element.find('h3', {'class': 'vkr-card__title'}).find('a').text
                    lecturer = ''
                    for second_element in element.find_all('p', {'class': 'vkr-card__item'}):
                        try:
                            lecturer = second_element.find('span', {'class': 'subCell'}).find('a').text
                        except:
                            lecturer = second_element.find('span', {'class': 'subCell'}).find('span', {
                                'class': 'vkr-card__value'}).text
                        finally:
                            continue
                    topic_name = topic_name.strip()
                    lecturer = lecturer.strip()
                    related_lecturer = User.objects.filter(first_name=lecturer.split()[1],
                                                            last_name=lecturer.split()[0],
                                                            profile__patronym=lecturer.split()[2],
                                                            profile__is_lecturer=True)
                    if related_lecturer.count() == 1:
                        if not Topic.objects.filter(name_russian=topic_name):
                            topic = Topic.objects.create(name_russian=topic_name,
                                                         lecturer=related_lecturer[0])
                            topic.save()
                    elif related_lecturer.count() == 0:
                        topic = Topic.objects.create(name_russian=topic_name,
                                                     description="Преподаватель ещё не зарегистрирован в системе."
                                                                 "Пишите на почту.")
                        topic.save()
                except:
                    print("An error occurred")
            page += 1
        else:
            if year <= now.year:
                year += 1
                page = 1
            else:
                break