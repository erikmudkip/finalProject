# Generated by Django 2.1.5 on 2019-02-18 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('IPC', '0007_auto_20190210_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyattendance',
            name='dailyAttendanceStudentStatus',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='IPC.AttendanceStatus'),
        ),
    ]
