# Generated by Django 2.1.5 on 2019-02-10 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IPC', '0006_auto_20190210_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancestatus',
            name='attendanceStatusName',
            field=models.CharField(max_length=255),
        ),
    ]
