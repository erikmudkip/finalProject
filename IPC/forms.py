from django import forms
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect

from .models import Announcement, Attendance, DailyAttendance, AttendanceStatus

class NewAnnouncementForm(forms.ModelForm):

    class Meta:
        model = Announcement
        fields = ['announcementFeed']

class NewAttendanceForm(forms.Form):
    statuses = get_list_or_404(AttendanceStatus)
    STATUS_LIST=[( (status.id), (status.attendanceStatusName) ) for status in statuses]

    studentStatus = forms.ChoiceField(choices=STATUS_LIST, initial=STATUS_LIST[0], widget=forms.RadioSelect)
