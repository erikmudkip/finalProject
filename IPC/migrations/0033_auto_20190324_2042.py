# Generated by Django 2.1.5 on 2019-03-24 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IPC', '0032_auto_20190323_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='attendanceDate',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
