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
        value = 0
        for attendance in attendances:
            if str(status.attendanceStatusName) == str(attendance.dailyAttendanceStudentStatus):
                value += 1
        if value != 0:
            plot_label.append(status.attendanceStatusName)
            plot_value.append(value)
    data_input = { 'labels': plot_label,
                   'values': plot_value,
                   'type': 'pie'}
    data = []
    data.append(data_input)
    layout = {'title': 'Student attendance based on status'}
    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
