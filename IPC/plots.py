import datetime
import glob
import logging
import os
from django.contrib.auth.models import User, Group

import numpy as np
import plotly.graph_objs as go
from plotly.offline import plot

from .models import *


def plotAttendance(username):
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

def plotGrade(username, subject_id, course_id):
    user_result_lists = list(Result.objects.filter(resultStudentId=username, resultSubject=subject_id, resultCourse=course_id))
    subjectName = Subject.objects.get(pk=subject_id)
    print(user_result_lists)
    xStudent = []
    xAverage = []
    yStudent = []
    yAverage = []
    for user_result_list in user_result_lists:
        counter = 0
        overall = 0
        students_result_lists = list(Result.objects.filter(resultReturnedDate=user_result_list.resultReturnedDate, resultName=user_result_list.resultName, resultOverallValue=user_result_list.resultOverallValue, resultSubject=user_result_list.resultSubject, resultCourse=user_result_list.resultCourse))
        print(students_result_lists)
        for students_result_list in students_result_lists:
            overall += int(students_result_list.resultStudentMark)
            counter += 1
        overall_average = overall / counter
        xStudent.append(user_result_list.resultName)
        xAverage.append(user_result_list.resultName)
        yStudent.append(user_result_list.resultStudentMark)
        yAverage.append(overall_average)
    traceStudent = go.Bar(x=xStudent,y=yStudent, name='Student Mark')
    traceAverage = go.Bar(x=xAverage,y=yAverage, name='Class Average Mark')
    data = [traceStudent, traceAverage]
    layout = go.Layout(
        # autosize=False,
        # width=900,
        # height=500,
        title='Student Grade Compared To Class Average for ' + str(subjectName.subjectName) + ' Subject',
        xaxis=dict(
            autorange=True
        ),
        yaxis=dict(
            autorange=True
        )
    )
    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
