# Generated by Django 3.2 on 2022-05-01 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20220430_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='interests',
            field=models.TextField(default='', verbose_name='Укажите свои интересы через запятую (например: машинное обучение, кибербезопасность)'),
        ),
    ]
