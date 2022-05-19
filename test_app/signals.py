import pandas as pd
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User # sender
from django.dispatch import receiver
from .models import Notification, Topic, StudentRequestForTopic, RequestResponse
from .views import process_query


@receiver(post_save, sender=StudentRequestForTopic)
def save_request(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(title='Новая заявка от студента',
                                    receiver=instance.associatedTopic.lecturer,
                                    content='%s отправил вам заявку на взаимодействие.'
                                        ' \nПроверьте её во вкладке "Заявки на темы от студентов"' % instance.student)

@receiver(post_save, sender=RequestResponse)
def save_response(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(title='Новый ответ на одну из ваших заявок',
                                    receiver=instance.associatedRequest.student,
                                    content='%s ответил вам по заявке.'
                                        ' \nПроверьте ответ во вкладке "Мои заявки на курсовые"' % instance.lecturer)

@receiver(post_save, sender=Topic)
def add_to_csv(sender, instance, created, **kwargs):
    if created:
        results = []
        results.append({
                'topic_id': instance.id,
                'topic': instance.name_russian,
                'lecturer': instance.lecturer.last_name,
                'lecturer_interests': instance.lecturer.profile.interests,
                'important_features': ' '.join(process_query(
                    instance.name_russian + ' ' + instance.lecturer.last_name + ' ' + instance.lecturer.profile.interests))
                })
        df = pd.DataFrame(data=results)

        df.to_csv('media/topic_db.csv', mode='a', header=False, index=False)

@receiver(post_delete, sender=Topic)
def delete_from_csv(sender, instance, **kwargs):
    df = pd.read_csv('media/topic_db.csv')
    df = df[df.topic_id != instance.id]
    df.to_csv('media/topic_db.csv', index=False)
