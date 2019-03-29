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
from django.utils.timezone import utc

from datetime import datetime, date, time, timedelta

from .models import *
from . import plots
from .forms import *

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
        results = list(Result.objects.filter(resultStudentId=request.user, resultReturnedDate=today).order_by('-resultReturnedDate'))
        announcements = Announcement.objects.filter(announcementDate__lte=date.today(), announcementDate__gt=date.today()-timedelta(days=7), announcementCourse=course_id).order_by('-announcementDate')
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
    results = list(Result.objects.filter(resultStudentId=student.id, resultReturnedDate=today).order_by('-resultReturnedDate'))
    announcements = Announcement.objects.filter(announcementDate__lte=date.today(), announcementDate__gt=date.today()-timedelta(days=7), announcementCourse=course_id).order_by('-announcementDate')
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
    announcements = list(Announcement.objects.filter(announcementCourse=course_id).order_by('-announcementDate'))
    return render(request, 'announcement.html', {'announcements': announcements,
                                                 'user_type': user_type,
                                                 'course_id': course_id,})


@login_required
def create_course_announcement(request, course_id):
    announcements = list(Announcement.objects.filter(announcementCourse=course_id).order_by('-announcementDate'))
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
        attendances = list(Attendance.objects.filter(attendanceCourseId=course_id).order_by('-attendanceDate'))
        current_subject = Subject.objects.get(subjectCourse = course_id, subjectTeacherId = request.user)
        last_attendance = Attendance.objects.filter(attendanceTeacherId=request.user, attendanceCourseId=course_id, attendanceSubject=current_subject).last()
        time_diff = (datetime.utcnow().replace(tzinfo=utc)-last_attendance.attendanceDate)
        seconds = time_diff.total_seconds()
        hours = seconds // 3600
        lock = "lock"
        if hours >= 1:
            lock = "unlock"
        return render(request, 'attendance.html', {'attendances': attendances,
                                                   'user_type': user_type,
                                                   'lock': lock,
                                                   'course_id': course_id,})
    elif user_type == "student":
        dailyAttendances = list(DailyAttendance.objects.filter(dailyAttendanceStudentId=request.user).order_by('-id'))
        attendances = list(Attendance.objects.filter(attendanceCourseId=course_id).order_by('-attendanceDate'))
        return render(request, 'attendance.html', {'dailyAttendances': dailyAttendances,
                                                   'attendances': attendances,
                                                   'user_type': user_type,
                                                   'course_id': course_id,
                                                   'data': zip(dailyAttendances,attendances)})


@login_required
def create_course_attendance(request, course_id):
    course = Course.objects.get(id=course_id)
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
        results = list(Result.objects.filter(resultStudentId=request.user).order_by('-resultReturnedDate'))
        return render(request, 'result.html', {'results': results,
                                               'user_type': user_type,
                                               'course_id': course_id,})
    elif user_type == "teacher":
        subject = Subject.objects.get(subjectCourse=course_id, subjectTeacherId=request.user)
        name = Result.objects.filter(resultCourse=course_id).first()
        results = list(Result.objects.filter(resultStudentId=name.resultStudentId, resultSubject=subject, resultCourse=course_id).order_by('-resultReturnedDate'))
        return render(request, 'result.html', {'results': results,
                                               'user_type': user_type,
                                               'course_id': course_id,})


@login_required
def course_result_detail(request, course_id, result_id):
    result_name = Result.objects.get(id=result_id)
    results = list(Result.objects.filter(resultName=result_name.resultName).order_by('resultName'))
    return render(request, 'result_detail.html', {'results': results,
                                                  'course_id': course_id,})


@login_required
def post_course_result(request, course_id):
    course = Course.objects.get(id=course_id)
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
            if str(form.cleaned_data.get('resultOverallValueInput')) == "None":
                resultOverallValueInput = 0
            else:
                resultOverallValueInput = form.cleaned_data.get('resultOverallValueInput')
            studentFormDatas = zip(students,formset)
            typeOfResult = ResultType.objects.get(id=resultTypeInput)
            for student, formse in studentFormDatas:
                if formset.is_valid():
                    if str(formse.cleaned_data.get('resultStudentMarkInput')) == "None":
                        resultStudentMarkInput = 0
                    else:
                        resultStudentMarkInput = formse.cleaned_data.get('resultStudentMarkInput')
                    resultFeedbackInput = formse.cleaned_data.get('resultFeedbackInput')
                    courseResult = Result.objects.create(resultOverallValue=resultOverallValueInput, resultSubject = currentSubject, resultType = typeOfResult, resultStudentId = student, resultStudentMark = resultStudentMarkInput, resultFeedback = resultFeedbackInput, resultCourse = course, resultName = resultNameInput)
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

@login_required
def institute_forum(request, course_id):
    course = Course.objects.get(id=course_id)
    forum_topics = list(ForumTopic.objects.filter(forumTopicInstitution = course.courseInstitution, forumTopicFlag = 0).order_by('-forumTopicPostedDate'))
    return render(request, 'institution_forum.html', {'course_id': course_id,
                                                    'forum_topics': forum_topics})


@login_required
def create_institute_topic(request, course_id):
    course = Course.objects.get(id=course_id)
    institution = Institution.objects.get(id=course.courseInstitution.id)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.forumTopicPoster = request.user
            topic.forumTopicInstitution = institution
            topic.forumTopicFlag = 0
            topic.save()
            return redirect('institute_forum', course_id=course_id)
    else:
        form = NewTopicForm()
    return render(request, 'create_topic.html', {'course_id': course_id,
                                                      'form': form})


@login_required
def delete_institute_topic(request, course_id, topic_id):
    topic = ForumTopic.objects.get(id=topic_id)
    topic.forumTopicFlag = 1
    topic.save()
    return redirect('institute_forum', course_id=course_id)


@login_required
def topic_post(request, course_id, topic_id):
    topic = ForumTopic.objects.get(id=topic_id)
    topic_posts = list(ForumTopicPost.objects.filter(forumTopicPostTopic = topic_id).order_by('-forumTopicPostCreatedTime'))
    return render(request, 'topic_post.html', {'course_id': course_id,
                                                'topic_id': topic_id,
                                                'topic': topic,
                                                'topic_posts': topic_posts,})


@login_required
def post_topic_post(request, course_id, topic_id):
    course = Course.objects.get(id=course_id)
    topic = ForumTopic.objects.get(id=topic_id)
    topic_posts = list(ForumTopicPost.objects.filter(forumTopicPostTopic = topic_id).order_by('-forumTopicPostCreatedTime'))[:5]
    if request.method == 'POST':
        form = NewTopicPostPost(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.forumTopicPostPoster = request.user
            post.forumTopicPostTopic = topic
            post.save()
            return redirect('topic_post', course_id=course_id, topic_id=topic_id)
    else:
        form = NewTopicPostPost()
    return render(request, 'post_topic_post.html', {'course_id': course_id,
                                                      'topic_id': topic_id,
                                                      'topic': topic,
                                                      'topic_posts': topic_posts,
                                                      'form': form})


@login_required
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

class edit_post_topic_post(UpdateView):
    model = ForumTopicPost
    fields = ('forumTopicPostPost', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.forumTopicPostUpdatedTime = datetime.now()
        post.save()
        return redirect('topic_post', course_id=post.forumTopicPostTopic.forumTopicCourse.pk, topic_id=post.forumTopicPostTopic.pk)
