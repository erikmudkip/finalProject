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
import calendar

from datetime import datetime, date, time, timedelta
from calendar import HTMLCalendar

from .utils import Calendar
from .models import *
from . import plots
from .forms import *

@login_required
def course(request):
    """Render the course page

    :param request: object that contains metadata about the request.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    courses = Course.objects.filter(courseCode__in=user.groups.values_list('name', flat=True))
    return render(request, 'course.html', {'courses': courses,
                                           'user_type': user_type,})


@login_required
def course_statistic(request, course_id, subject_id = "none"):
    """Render the analytics page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param subject_id: object that contain the ID of a subject in the course.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    course = Course.objects.get(id=course_id)
    today = date.today()
    if user_type == "student":
        subjects = list(Subject.objects.filter(subjectCourse=course_id))
        results = list(Result.objects.filter(resultStudentId=request.user, resultReturnedDate=today).order_by('-resultReturnedDate'))
        events = Event.objects.filter(eventDate__lte=date.today()+timedelta(days=7), eventDate__gt=date.today(), eventCourse=course_id).order_by('eventDate')
        today = date.today()
        eventsToday = Event.objects.filter(eventDate=date.today(), eventCourse=course_id).order_by('eventDate')
        announcements = Announcement.objects.filter(announcementDate__lte=date.today(), announcementDate__gt=date.today()-timedelta(days=7), announcementCourse=course_id).order_by('-announcementDate')
        username = request.user
        if subject_id == "none":
            plot = plots.plotAttendance(username)
        else:
            subject = Subject.objects.get(pk=subject_id)
            plot = plots.plotGrade(username, subject.pk, course_id)
        return render(request, 'statistic.html', {'course_id': course_id,
                                                  'results': results,
                                                  'announcements': announcements,
                                                  'user_type': user_type,
                                                  'subjects': subjects,
                                                  'events': events,
                                                  'today': today,
                                                  'eventsToday': eventsToday,
                                                  'plot': plot})
    elif user_type == "teacher":
         students = list(User.objects.filter(groups__name=course.courseCode).filter(groups__name='Student'))
         return render(request, 'statistic.html', {'course_id': course_id,
                                                   'students': students,
                                                   'user_type': user_type,})


@login_required
def course_student_statistic(request, course_id, user_id, subject_id = "none"):
    """Render the student page when a teacher click the button in the analytics page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param user_id: object that contain the ID of the student picked at analytics page.
    :param subject_id: object that contain the ID of a subject in the course.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    course = Course.objects.get(id=course_id)
    today = date.today()
    student = User.objects.get(id=user_id)
    results = list(Result.objects.filter(resultStudentId=student.id, resultReturnedDate=today).order_by('-resultReturnedDate'))
    announcements = Announcement.objects.filter(announcementDate__lte=date.today(), announcementDate__gt=date.today()-timedelta(days=7), announcementCourse=course_id).order_by('-announcementDate')
    events = Event.objects.filter(eventDate__lte=date.today()+timedelta(days=7), eventDate__gt=date.today(), eventCourse=course_id).order_by('eventDate')
    today = date.today()
    eventsToday = Event.objects.filter(eventDate=date.today(), eventCourse=course_id).order_by('eventDate')
    username = student
    subjects = list(Subject.objects.filter(subjectCourse=course_id))
    if subject_id == "none":
        plot = plots.plotAttendance(username)
    else:
        subject = Subject.objects.get(pk=subject_id)
        plot = plots.plotGrade(username, subject.pk, course_id)
    return render(request, 'student_statistic.html', {'course_id': course_id,
                                                      'results': results,
                                                      'announcements': announcements,
                                                      'subjects': subjects,
                                                      'events': events,
                                                      'today': today,
                                                      'eventsToday': eventsToday,
                                                      'plot': plot,
                                                      'student': student,})


@login_required
def course_announcement(request, course_id):
    """Render the announcements page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
    """Render the page to post an announcement.

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
    """Render the attendance page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    if user_type == "teacher":
        attendances = list(Attendance.objects.filter(attendanceCourseId=course_id).order_by('-attendanceDate'))
        current_subject = Subject.objects.get(subjectCourse = course_id, subjectTeacherId = request.user)
        last_attendance = Attendance.objects.filter(attendanceTeacherId=request.user, attendanceCourseId=course_id, attendanceSubject=current_subject).last()
        if not last_attendance:
            lock = "unlock"
        else:
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
    """Render the page used to create an attendance

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
    """Render a detailed page of a certain attendance

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param attendance_id: object that contain the ID of the attendance picked at attendance page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    attendancesDetails = list(DailyAttendance.objects.filter(dailyAttendanceAttendanceId=attendance_id).order_by('dailyAttendanceStudentId'))
    return render(request, 'attendance_detail.html', {'attendancesDetails': attendancesDetails,
                                                      'course_id': course_id,})


@login_required
def course_result(request, course_id):
    """Render the result page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
        if name:
            results = list(Result.objects.filter(resultStudentId=name.resultStudentId, resultSubject=subject, resultCourse=course_id).order_by('-resultReturnedDate'))
        else:
            results = []
        return render(request, 'result.html', {'results': results,
                                               'user_type': user_type,
                                               'course_id': course_id,})


@login_required
def course_result_detail(request, course_id, result_id):
    """Render a detailed page of a certain result

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param result_id: object that contain the ID of the result picked at result page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    result_name = Result.objects.get(id=result_id)
    results = list(Result.objects.filter(resultName=result_name.resultName).order_by('resultName'))
    return render(request, 'result_detail.html', {'results': results,
                                                  'course_id': course_id,})


@login_required
def post_course_result(request, course_id):
    """Render the page used to post a result

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
    """Render a page containing all the material posted in the course

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
    """Render a page used to post a material

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
    """Render a page used by the user to discuss a material posted in the course

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param material_id: object that contain the ID of the material picked at material page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    material = Material.objects.get(id=material_id)
    discussions = list(Discussion.objects.filter(discussionMaterial = material_id, discussionCourse = course_id).order_by('-discussionCreatedTime'))
    return render(request, 'discussion.html', {'course_id': course_id,
                                                'material_id': material_id,
                                             'material': material,
                                             'discussions': discussions,})


@login_required
def post_material_discussion(request, course_id, material_id):
    """Render a page used to post a discussion for discussion page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param material_id: object that contain the ID of the material picked at material page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
    """Render a forum that can be used by all member of an institution

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    course = Course.objects.get(id=course_id)
    forum_topics = list(ForumTopic.objects.filter(forumTopicInstitution = course.courseInstitution, forumTopicFlag = 0).order_by('-forumTopicPostedDate'))
    return render(request, 'institution_forum.html', {'course_id': course_id,
                                                    'forum_topics': forum_topics})


@login_required
def create_institute_topic(request, course_id):
    """Render a page used by user to create a topic in the forum page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    course = Course.objects.get(id=course_id)
    institution = Institution.objects.get(id=course.courseInstitution.id)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.forumTopicPoster = request.user
            topic.forumTopicInstitution = institution
            topic.forumTopicFlag = 0
            topic.forumTopicCourse = course
            topic.save()
            return redirect('institute_forum', course_id=course_id)
    else:
        form = NewTopicForm()
    return render(request, 'create_topic.html', {'course_id': course_id,
                                                      'form': form})


@login_required
def delete_institute_topic(request, course_id, topic_id):
    """Render a page used by user to delete a topic the user created in the forum page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param topic_id: object that contain the ID of the topic that the user created.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    topic = ForumTopic.objects.get(id=topic_id)
    topic.forumTopicFlag = 1
    topic.save()
    return redirect('institute_forum', course_id=course_id)


@login_required
def topic_post(request, course_id, topic_id):
    """Render a page where user can discuss the heading and put comments

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param topic_id: object that contain the ID of the topic that the user created.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    topic = ForumTopic.objects.get(id=topic_id)
    topic_posts = list(ForumTopicPost.objects.filter(forumTopicPostTopic = topic_id).order_by('-forumTopicPostCreatedTime'))
    return render(request, 'topic_post.html', {'course_id': course_id,
                                                'topic_id': topic_id,
                                                'topic': topic,
                                                'topic_posts': topic_posts,})


@login_required
def post_topic_post(request, course_id, topic_id):
    """Render a page used by user to post a comment in a topic inside the forum page

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param topic_id: object that contain the ID of the topic that the user created.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
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
    """Render a page used by user to post a comment in a topic inside the forum page

    :param request: object that contains metadata about the request.
    :param file_name: object that contain the path of a certain material.

    :returns: response (allow user to download material from the materials page).
    """
    file_path = settings.MEDIA_ROOT +'/'+ file_name
    file_wrapper = FileWrapper(file(file_path,'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype )
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    return response


class edit_material_discussion(UpdateView):
    """Render a page used by user to edit a comment in the discussion page

    :param UpdateView: used to update an existing object.

    :returns: An HTML url and object that's specified.
    """
    model = Discussion
    fields = ('discussionPost', )
    template_name = 'edit_discussion.html'
    pk_url_kwarg = 'discussion_id'
    context_object_name = 'discussion'

    def form_valid(self, form):
        """redirect user to material page when form is valid

        :param self: object that contains metadata about the request.
        :param form: form that was filled by the user and posted to the views to be processed.

        :returns: redirect (direct user to a different page.).
        """
        discussion = form.save(commit=False)
        discussion.discussionUpdatedTime = datetime.now()
        discussion.save()
        return redirect('material_discussion', course_id=discussion.discussionCourse.pk, material_id=discussion.discussionMaterial.pk)

class edit_post_topic_post(UpdateView):
    """Render a page used by user to edit a post in the forum page

    :param UpdateView: used to update an existing object.

    :returns: An HTML url and object that's specified.
    """
    model = ForumTopicPost
    fields = ('forumTopicPostPost', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def form_valid(self, form):
        """redirect user to material page when form is valid

        :param self: object that contains metadata about the request.
        :param form: form that was filled by the user and posted to the views to be processed.

        :returns: redirect (direct user to a different page.).
        """
        post = form.save(commit=False)
        post.forumTopicPostUpdatedTime = datetime.now()
        post.save()
        return redirect('topic_post', course_id=post.forumTopicPostTopic.forumTopicCourse.pk, topic_id=post.forumTopicPostTopic.pk)

class course_calendar(generic.ListView):
    """create the calendar page

    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

    :param self: object that contains metadata about the request.
    :param form: form that was filled by the user and posted to the views to be processed.

    :returns: redirect (direct user to a different page.).
    """
    model = Event
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        user = self.request.user
        if user.groups.filter(name='Teacher').exists():
            user_type = "teacher"
        elif user.groups.filter(name='Student').exists():
            user_type = "student"
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, course_id, user_type)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return {'context': context, 'course_id': course_id, 'user_type': user_type}

def get_date(req_month):
    """get date for the calendar page

    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

    :param req_month: object that contain name of a month.

    :returns: datetime.today() (return the current date and time.).
    """
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    """get previous month for the calendar page

    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

    :param d: object that contain the current date, month and year.

    :returns: month (return the previous month name.).
    """
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    """get the next month for the calendar page

    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

    :param d: object that contain the current date, month and year.

    :returns: month (return the next month name.).
    """
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def course_event(request, course_id, event_id=None):
    """create or show event based on parameter

    .. note::This code was made by following this tutorial "https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html". Some part of the code is change in order to be able to be integrated to the webapp

    :param request: object that contains metadata about the request.
    :param course_id: object that contain the ID of the course picked at course page.
    :param event_id: object that contain the ID of an event.

    :returns: month (return the next month name.).
    """
    user = request.user
    if user.groups.filter(name='Teacher').exists():
        user_type = "teacher"
    elif user.groups.filter(name='Student').exists():
        user_type = "student"
    instance = Event()
    if event_id:
        instance = get_object_or_404(Event, pk=event_id, eventCourse=course_id)
    else:
        instance = Event()

    course = Course.objects.get(id=course_id)
    form = EventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        event = form.save(commit=False)
        event.eventCourse = course
        event.save()
        if event_id:
            announcementMessege = str(instance.eventTitle) + " has been updated in the calendar"
            announcementPost = Announcement.objects.create(announcementPosterId = request.user, announcementCourse = course, announcementFeed = announcementMessege)
        else:
            announcementMessege = "New event has just been added to the calendar"
            announcementPost = Announcement.objects.create(announcementPosterId = request.user, announcementCourse = course, announcementFeed = announcementMessege)
        return redirect('calendar', course_id=course_id)
    return render(request, 'event.html', {'form': form,
                                            'user_type': user_type,
                                          'course_id': course_id,})
