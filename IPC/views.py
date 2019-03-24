from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User, Group
from django.forms import formset_factory
from django.views import generic
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView
from django.views.static import serve

from datetime import datetime, date, time, timedelta

from .models import *
from . import plots
from .forms import NewAnnouncementForm, NewAttendanceForm, NewResultForm, NewResultMarkForm, NewDocumentForm, NewDiscussionForm
#from .utils import Calendar

@login_required
def course(request):
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    courses = Course.objects.filter(courseCode__in=user.groups.values_list('name', flat=True))
    return render(request, 'course.html', {'courses': courses,
                                           'user_type': user_type,})


@login_required
def course_statistic(request, course_id):
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    course = Course.objects.get(id=course_id)
    today = date.today()
    if user_type == "student":
        #results = get_list_or_404(Result.objects.order_by('-resultReturnedDate'), resultStudentId=request.user, resultReturnedDate=today)
        results = list(Result.objects.filter(resultStudentId=request.user, resultReturnedDate=today).order_by('-resultReturnedDate'))
        announcements = Announcement.objects.filter(announcementDate__lte=date.today(), announcementDate__gt=date.today()-timedelta(days=7), announcementCourse=course_id)
        username = request.user
        plot = plots.plot1d(username)
        return render(request, 'statistic.html', {'course_id': course_id,
                                                  'results': results,
                                                  'announcements': announcements,
                                                  'user_type': user_type,
                                                  'plot': plot})
    elif user_type == "teacher":
         students = list(User.objects.filter(groups__name=course.courseCode).filter(groups__name='Student'))
         return render(request, 'statistic.html', {'course_id': course_id,
                                                   'students': students,
                                                   'user_type': user_type,})


@login_required
def course_student_statistic(request, course_id, user_id):
    course = Course.objects.get(id=course_id)
    today = date.today()
    student = User.objects.get(id=user_id)
    #results = get_list_or_404(Result.objects.order_by('-resultReturnedDate'), resultStudentId=request.user, resultReturnedDate=today)
    results = list(Result.objects.filter(resultStudentId=student.id, resultReturnedDate=today).order_by('-resultReturnedDate'))
    announcements = Announcement.objects.filter(announcementDate__lte=date.today(), announcementDate__gt=date.today()-timedelta(days=7), announcementCourse=course_id)
    username = student
    plot = plots.plot1d(username)
    return render(request, 'student_statistic.html', {'course_id': course_id,
                                                      'results': results,
                                                      'announcements': announcements,
                                                      'plot': plot,
                                                      'student': student,})


@login_required
def course_announcement(request, course_id):
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    #announcements = get_list_or_404(Announcement.objects.order_by('-announcementDate'), announcementCourse=course_id)
    announcements = list(Announcement.objects.filter(announcementCourse=course_id).order_by('-announcementDate'))
    return render(request, 'announcement.html', {'announcements': announcements,
                                                 'user_type': user_type,
                                                 'course_id': course_id,})


@login_required
def create_course_announcement(request, course_id):
    #announcements = get_list_or_404(Announcement.objects.order_by('-announcementDate'), announcementCourse=course_id)
    announcements = list(Announcement.objects.filter(announcementCourse=course_id).order_by('-announcementDate'))
    #course = get_object_or_404(Course, id=course_id)
    course = Course.objects.get(id=course_id)
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


@login_required
def course_attendance(request, course_id):
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    if user_type == "teacher":
        #attendances = get_list_or_404(Attendance.objects.order_by('-attendanceDate'), attendanceCourseId=course_id)
        attendances = list(Attendance.objects.filter(attendanceCourseId=course_id).order_by('-attendanceDate'))
        return render(request, 'attendance.html', {'attendances': attendances,
                                                   'user_type': user_type,
                                                   'course_id': course_id,})
    elif user_type == "student":
        #dailyAttendances = get_list_or_404(DailyAttendance.objects.order_by('-id'), dailyAttendanceStudentId=request.user)
        dailyAttendances = list(DailyAttendance.objects.filter(dailyAttendanceStudentId=request.user).order_by('-id'))
        #attendances = get_list_or_404(Attendance.objects.order_by('-attendanceDate'))
        attendances = list(Attendance.objects.filter(attendanceCourseId=course_id).order_by('-attendanceDate'))
        return render(request, 'attendance.html', {'dailyAttendances': dailyAttendances,
                                                   'attendances': attendances,
                                                   'user_type': user_type,
                                                   'course_id': course_id,
                                                   'data': zip(dailyAttendances,attendances)})


@login_required
def create_course_attendance(request, course_id):
    #course = get_object_or_404(Course, id=course_id)
    course = Course.objects.get(id=course_id)
    #currentSubject = get_object_or_404(Subject, subjectCourse = course_id, subjectTeacherId = request.user)
    currentSubject = Subject.objects.get(subjectCourse = course_id, subjectTeacherId = request.user)
    students = User.objects.filter(groups__name=course.courseCode).filter(groups__name='Student')
    studentNumber = students.count()
    studentStatusFormSet = formset_factory(NewAttendanceForm, extra=studentNumber, max_num=500)
    if request.method == 'POST':
        formset = studentStatusFormSet(request.POST)
        if formset.is_valid():
            attendance = Attendance.objects.create(attendanceTeacherId=request.user, attendanceCourseId=course, attendanceSubject=currentSubject)
            attendanceId = Attendance.objects.order_by('-pk')[0]
            studentFormDatas = zip(students,formset)
            for student, form in studentFormDatas:
                studentStatus = form.cleaned_data.get('studentStatus')
                #statusTake = get_object_or_404(AttendanceStatus, id=studentStatus)
                statusTake = AttendanceStatus.objects.get(id=studentStatus)
                dailyattendance = DailyAttendance.objects.create(dailyAttendanceStudentId = student, dailyAttendanceStudentStatus = statusTake, dailyAttendanceAttendanceId = attendanceId)
        return redirect('course_attendance', course_id=course_id)
    else:
        formset = studentStatusFormSet()
    return render(request, 'create_attendance.html', {'students': students,
                                                      'course_id': course_id,
                                                      'formset': formset,
                                                      'data': zip(students, formset)})


@login_required
def course_attendance_detail(request, course_id, attendance_id):
    #attendancesDetails = get_list_or_404(DailyAttendance.objects.order_by('dailyAttendanceStudentId'), dailyAttendanceAttendanceId=attendance_id)
    attendancesDetails = list(DailyAttendance.objects.filter(dailyAttendanceAttendanceId=attendance_id).order_by('dailyAttendanceStudentId'))
    return render(request, 'attendance_detail.html', {'attendancesDetails': attendancesDetails,
                                                      'course_id': course_id,})


@login_required
def course_result(request, course_id):
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    if user_type == "student":
        #results = get_list_or_404(Result.objects.order_by('-resultReturnedDate'), resultStudentId=request.user)
        results = list(Result.objects.filter(resultStudentId=request.user).order_by('-resultReturnedDate'))
        return render(request, 'result.html', {'results': results,
                                               'user_type': user_type,
                                               'course_id': course_id,})
    elif user_type == "teacher":
        subject = Subject.objects.get(subjectCourse=course_id, subjectTeacherId=request.user)
        name = Result.objects.filter(resultCourse=course_id).first()
        #results = get_list_or_404(Result.objects.order_by('-resultReturnedDate'), resultStudentId=name.resultStudentId)
        results = list(Result.objects.filter(resultStudentId=name.resultStudentId, resultSubject=subject, resultCourse=course_id).order_by('-resultReturnedDate'))
        return render(request, 'result.html', {'results': results,
                                               'user_type': user_type,
                                               'course_id': course_id,})


@login_required
def course_result_detail(request, course_id, result_id):
    #result_name = get_object_or_404(Result, id=result_id)
    result_name = Result.objects.get(id=result_id)
    #results = get_list_or_404(Result.objects.order_by('resultName'), resultName=result_name.resultName)
    results = list(Result.objects.filter(resultName=result_name.resultName).order_by('resultName'))
    return render(request, 'result_detail.html', {'results': results,
                                                  'course_id': course_id,})


@login_required
def post_course_result(request, course_id):
    #course = get_object_or_404(Course, id=course_id)
    course = Course.objects.get(id=course_id)
    #currentSubject = get_object_or_404(Subject, subjectCourse = course_id, subjectTeacherId = request.user)
    currentSubject = Subject.objects.get(subjectCourse = course_id, subjectTeacherId = request.user)
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
            #typeOfResult = get_object_or_404(ResultType, id=resultTypeInput)
            typeOfResult = ResultType.objects.get(id=resultTypeInput)
            for student, formse in studentFormDatas:
                if formset.is_valid():
                    if str(formse.cleaned_data.get('resultStudentMarkInput')) == "None":
                        resultStudentMarkInput = 0
                    else:
                        resultStudentMarkInput = formse.cleaned_data.get('resultStudentMarkInput')
                    resultFeedbackInput = formse.cleaned_data.get('resultFeedbackInput')
                    courseResult = Result.objects.create(resultSubject = currentSubject, resultType = typeOfResult, resultStudentId = student, resultStudentMark = resultStudentMarkInput, resultFeedback = resultFeedbackInput, resultCourse = course, resultName = resultNameInput)
            announcementMessege = "The " + str(typeOfResult) + " result of " + str(resultNameInput) + " is now available!"
            announcementPost = Announcement.objects.create(announcementPosterId = request.user, announcementCourse = course, announcementFeed = announcementMessege)
        return redirect('course_result', course_id=course_id)
    else:
        form = NewResultForm()
        formset = studentMarkFormSet()
    return render(request, 'create_result.html', {'students': students,
                                                  'course_id': course_id,
                                                  'formset': formset,
                                                  'form': form,
                                                  'data': zip(students, formset)})



@login_required
def course_material(request, course_id):
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    materials = list(Material.objects.filter(materialCourse=course_id).order_by('-materialUploadTime'))
    return render(request, 'material.html', {'course_id': course_id,
                                              'materials': materials,
                                              'user_type': user_type})


@login_required
def post_course_material(request, course_id):
    course = Course.objects.get(id=course_id)
    currentSubject = Subject.objects.get(subjectCourse = course_id, subjectTeacherId = request.user)
    if request.method == 'POST':
        form = NewDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.materialCourse = course
            document.materialSubject =  currentSubject
            document.materialPosterId = request.user
            document.save()
            return redirect('course_material', course_id=course_id)
    else:
        form = NewDocumentForm()
    return render(request, 'create_material.html', {'course_id': course_id,
                                                    'form': form})


@login_required
def material_discussion(request, course_id, material_id):
    material = Course.objects.get(id=material_id)
    discussions = list(Discussion.objects.filter(discussionMaterial = material_id, discussionCourse = course_id).order_by('-discussionCreatedTime'))
    return render(request, 'discussion.html', {'course_id': course_id,
                                                'material_id': material_id,
                                             'material': material,
                                             'discussions': discussions,})


@login_required
def post_material_discussion(request, course_id, material_id):
    course = Course.objects.get(id=course_id)
    material = Material.objects.get(id=material_id)
    discussions = list(Discussion.objects.filter(discussionMaterial = material_id, discussionCourse = course_id).order_by('-discussionCreatedTime'))[:5]
    if request.method == 'POST':
        form = NewDiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.discussionMaterial = material
            discussion.discussionPoster = request.user
            discussion.discussionCourse = course
            discussion.save()
            return redirect('material_discussion', course_id=course_id, material_id=material_id)
    else:
        form = NewDiscussionForm()
    return render(request, 'create_discussion.html', {'course_id': course_id,
                                                      'material_id': material_id,
                                                      'discussions': discussions,
                                                      'form': form})


def download(request,file_name):
    file_path = settings.MEDIA_ROOT +'/'+ file_name
    file_wrapper = FileWrapper(file(file_path,'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype )
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    return response


class edit_material_discussion(UpdateView):
    model = Discussion
    fields = ('discussionPost', )
    template_name = 'edit_discussion.html'
    pk_url_kwarg = 'discussion_id'
    context_object_name = 'discussion'

    def form_valid(self, form):
        discussion = form.save(commit=False)
        discussion.discussionUpdatedTime = datetime.now()
        discussion.save()
        return redirect('material_discussion', course_id=discussion.discussionCourse.pk, material_id=discussion.discussionMaterial.pk)

#def course_calendar(request, course_id):
#    user = request.user
#    if user.groups.filter(name='Teacher').exists():
#        user_type = "teacher"
#    elif user.groups.filter(name='Student').exists():
#        user_type = "student"
#    #exams = get_list_or_404(ExamDate.objects.order_by('-examDateDate'), examDateCourse=course_id)
#    exams = list(ExamDate.objects.filter(examDateCourse=course_id).order_by('-examDateDate'))
#    #assigntments = get_list_or_404(AssigntmentDeadline.objects.order_by('-assigntmentDeadlineDueDate'), assigntmentDeadlineCourse=course_id)
#    assigntments = list(AssigntmentDeadline.objects.filter(assigntmentDeadlineCourse=course_id).order_by('-assigntmentDeadlineDueDate'))
#    return render(request, 'calendar.html', {'exams': exams,
#                                             'assigntments': assigntments,
#                                             'user_type': user_type,
#                                             'course_id': course_id,})

#class CalendarView(generic.ListView):
#    model = Event
#    template_name = 'calendar.html'

#    def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
#        d = get_date(self.request.GET.get('day', None))

#        # Instantiate our calendar class with today's year and date
#        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
#        html_cal = cal.formatmonth(withyear=True)
#        context['calendar'] = mark_safe(html_cal)
#        return context

#def get_date(req_day):
#    if req_day:
#        year, month = (int(x) for x in req_day.split('-'))
#        return date(year, month, day=1)
#    return datetime.today()
