# Generated by Django 2.1.5 on 2019-02-27 16:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IPC', '0019_auto_20190227_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assigntmentdeadline',
            name='assigntmentDeadlineDueDate',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 27, 16, 30, 57, 338601)),
        ),
        migrations.AlterField(
            model_name='examdate',
            name='examDateDate',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 27, 16, 30, 57, 339599)),
        ),
        migrations.AlterField(
            model_name='result',
            name='resultFeedback',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
