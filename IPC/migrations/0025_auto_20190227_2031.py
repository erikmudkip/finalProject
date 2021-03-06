# Generated by Django 2.1.5 on 2019-02-27 20:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IPC', '0024_auto_20190227_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='announcementDate',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='assigntmentdeadline',
            name='assigntmentDeadlineDueDate',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 27, 20, 31, 28, 3097)),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='attendanceDate',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='examdate',
            name='examDateDate',
            field=models.DateTimeField(default=datetime.datetime(2019, 2, 27, 20, 31, 28, 4094)),
        ),
        migrations.AlterField(
            model_name='result',
            name='resultReturnedDate',
            field=models.DateField(auto_now_add=True),
        ),
    ]
