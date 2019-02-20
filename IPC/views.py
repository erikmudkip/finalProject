from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User, Group
from django.forms import formset_factory


import datetime

from .models import Institution, Attendance, DailyAttendance, AttendanceStatus, Announcement, Course, Result, ResultType
from .forms import NewAnnouncementForm, NewAttendanceForm, NewResultForm, NewResultMarkForm


def course(request):
    courses = Course.objects.all()
    return render(request, 'course.html', {'courses': courses})

def course_statistic(request, course_id):
    results = get_list_or_404(Result.objects.order_by('-resultReturnedDate'), resultStudentId=request.user)
    dailyAttendances = get_list_or_404(DailyAttendance.objects.order_by('-id'), dailyAttendanceStudentId=request.user)
    attendances = get_list_or_404(Attendance.objects.order_by('-attendanceDate'))
    return render(request, 'statistic.html', {'course_id': course_id,
                                              'results': results,
                                              'dailyAttendances': dailyAttendances,
                                              'attendances': attendances,
                                              'data': zip(dailyAttendances,attendances)})

def course_announcement(request, course_id):
    announcements = get_list_or_404(Announcement.objects.order_by('-announcementDate'), announcementCourse=course_id)
    return render(request, 'announcement.html', {'announcements': announcements,
                                                 'course_id': course_id,})

def create_course_announcement(request, course_id):
    announcements = get_list_or_404(Announcement.objects.order_by('-announcementDate'), announcementCourse=course_id)
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = NewAnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.announcementCourse = course
            announcement.announcementPosterId = request.user
            announcement.save()
            return redirect('course_announcement', course_id=course_id)
    else:
        form = NewAnnouncementForm()
    return render(request, 'create_announcement.html', {'course_id': course_id,
                                                         'form': form})

def course_attendance(request, course_id):
    attendances = get_list_or_404(Attendance.objects.order_by('-attendanceDate'), attendanceCourseId=course_id)
    return render(request, 'attendance.html', {'attendances': attendances,
                                                      'course_id': course_id,})

def create_course_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = User.objects.filter(groups__name=course.courseCode).filter(groups__name='Student')
    studentNumber = students.count()
    studentStatusFormSet = formset_factory(NewAttendanceForm, extra=studentNumber, max_num=500)
    if request.method == 'POST':
        formset = studentStatusFormSet(request.POST)
        if formset.is_valid():
            attendance = Attendance.objects.create(attendanceTeacherId=request.user, attendanceCourseId=course)
            attendanceId = Attendance.objects.order_by('-pk')[0]
            studentFormDatas = zip(students,formset)
            for student, form in studentFormDatas:
                studentStatus = form.cleaned_data.get('studentStatus')
                statusTake = get_object_or_404(AttendanceStatus, id=studentStatus)
                dailyattendance = DailyAttendance.objects.create(dailyAttendanceStudentId = student, dailyAttendanceStudentStatus = statusTake, dailyAttendanceAttendanceId = attendanceId)
        return redirect('course_attendance', course_id=course_id)
    else:
        formset = studentStatusFormSet()
    return render(request, 'create_attendance.html', {'students': students,
                                                      'course_id': course_id,
                                                      'formset': formset,
                                                      'data': zip(students, formset)})

def course_attendance_detail(request, course_id, attendance_id):
    attendancesDetails = get_list_or_404(DailyAttendance.objects.order_by('dailyAttendanceStudentId'), dailyAttendanceAttendanceId=attendance_id)
    return render(request, 'attendance_detail.html', {'attendancesDetails': attendancesDetails,
                                                      'course_id': course_id,})

def course_result(request, course_id):
    results = get_list_or_404(Result.objects.order_by('-resultReturnedDate'), resultStudentId=request.user)
    return render(request, 'result.html', {'results': results,
                                            'course_id': course_id,})

def post_course_result(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = User.objects.filter(groups__name=course.courseCode).filter(groups__name='Student')
    studentNumber = students.count()
    studentMarkFormSet = formset_factory(NewResultMarkForm, extra=studentNumber, max_num=500)
    if request.method == 'POST':
        form = NewResultForm(request.POST)
        formset = studentMarkFormSet(request.POST)
        if form.is_valid():
            resultTypeInput = form.cleaned_data.get('resultTypeInput')
            resultNameInput = form.cleaned_data.get('resultNameInput')
            studentFormDatas = zip(students,formset)
            typeOfResult = get_object_or_404(ResultType, id=resultTypeInput)
            for student, formse in studentFormDatas:
                if formset.is_valid():
                    resultStudentMarkInput = formse.cleaned_data.get('resultStudentMarkInput')
                    resultFeedbackInput = formse.cleaned_data.get('resultFeedbackInput')
                    courseResult = Result.objects.create(resultType = typeOfResult, resultStudentId = student, resultStudentMark = resultStudentMarkInput, resultFeedback = resultFeedbackInput, resultCourse = course, resultName = resultNameInput)
        return redirect('course_result', course_id=course_id)
    else:
        form = NewResultForm()
        formset = studentMarkFormSet()
    return render(request, 'create_result.html', {'students': students,
                                                      'course_id': course_id,
                                                      'formset': formset,
                                                      'form': form,
                                                      'data': zip(students, formset)})
