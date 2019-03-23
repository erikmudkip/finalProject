import datetime
import glob
import logging
import os
from django.contrib.auth.models import User, Group

import numpy as np
import plotly.graph_objs as go
from plotly.offline import plot

from .models import *


def plot1d(username):
    attendances = list(DailyAttendance.objects.filter(dailyAttendanceStudentId=username))
    student_status = list(AttendanceStatus.objects.filter())
    plot_label = []
    plot_value = []
    for status in student_status:
        plot_label.append(status.attendanceStatusName)
        value = 0
        for attendance in attendances:
            print(attendance)
            print('start 0')
            if str(status.attendanceStatusName) == str(attendance.dailyAttendanceStudentStatus):
                value += 1
                print("value " + str(value))
        print("value appended " + str(value))
        plot_value.append(value)
    print(plot_value)
    data_input = { 'labels': plot_label,
             'values': plot_value,
             'type': 'pie'}
    data = []
    data.append(data_input)
    layout = {'title': 'Student attendance based on status'}
    fig = go.Figure(data=data, layout=layout)
    print(fig)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
