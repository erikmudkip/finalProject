# Generated by Django 2.1.5 on 2019-03-29 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IPC', '0035_forumtopic_forumtopicpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumtopic',
            name='forumTopicDesc',
            field=models.TextField(default=1, max_length=4000),
            preserve_default=False,
        ),
    ]
