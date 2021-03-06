# Generated by Django 2.1.5 on 2019-03-11 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IPC', '0026_auto_20190306_1316'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('materialTitle', models.CharField(blank=True, max_length=255)),
                ('materialDescription', models.TextField(max_length=4000)),
                ('materialDocument', models.FileField(upload_to='documents/')),
                ('materialUploadTime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Event',
        ),
    ]
