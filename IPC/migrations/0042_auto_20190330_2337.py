# Generated by Django 2.1.5 on 2019-03-30 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IPC', '0041_auto_20190330_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='resultFeedback',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]