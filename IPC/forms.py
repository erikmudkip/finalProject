from django import forms
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ModelForm, DateInput


from .models import *

class NewAnnouncementForm(forms.ModelForm):

    class Meta:
        model = Announcement
        fields = ['announcementFeed']

class NewAttendanceForm(forms.Form):
    statuses = get_list_or_404(AttendanceStatus)
    STATUS_LIST=[( (status.id), (status.attendanceStatusName) ) for status in statuses]

    studentStatus = forms.ChoiceField(choices=STATUS_LIST, initial=STATUS_LIST[0], widget=forms.RadioSelect)

class NewResultForm(forms.Form):
    resultTypes = get_list_or_404(ResultType)
    RESULT_TYPE_LIST=[( (resultType.id), (resultType.ResultTypeName) ) for resultType in resultTypes]

    resultTypeInput = forms.ChoiceField(choices=RESULT_TYPE_LIST, initial=RESULT_TYPE_LIST[0], widget=forms.RadioSelect)
    resultNameInput = forms.CharField(max_length=255)
    resultOverallValueInput = forms.IntegerField(initial=0, max_value=100, min_value=0)

class NewResultMarkForm(forms.Form):

    resultStudentMarkInput = forms.IntegerField(initial=0, max_value=100, min_value=0)
    resultFeedbackInput = forms.CharField(max_length=255,initial="None")

class NewDocumentForm(forms.ModelForm):

    class Meta:
        model = Material
        fields = ('materialTitle', 'materialDescription', 'materialDocument',)

class NewDiscussionForm(forms.ModelForm):

    class Meta:
        model = Discussion
        fields = ['discussionPost', ]

class NewTopicForm(forms.ModelForm):

    class Meta:
        model = ForumTopic
        fields = ('forumTopicName', 'forumTopicDesc')

class NewTopicPostPost(forms.ModelForm):

    class Meta:
        model = ForumTopicPost
        fields = ['forumTopicPostPost', ]

class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['eventTitle','eventDescription','eventDate','eventTime', ]
