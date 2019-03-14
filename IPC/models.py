from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from datetime import datetime

class Institution(models.Model):
    institutionName = models.CharField(max_length=255)
    institutionCode = models.CharField(max_length=255)

    def __str__(self):
        return self.institutionName


class Course(models.Model):
    courseName = models.CharField(max_length=255)
    courseCode= models.CharField(max_length=255)
    courseInstitution = models.ForeignKey(Institution, on_delete=models.CASCADE,)

    def __str__(self):
        return self.courseCode

class Subject(models.Model):
    subjectName = models.CharField(max_length=255)
    subjectCourse = models.ForeignKey(Course, on_delete=models.CASCADE)
    subjectTeacherId = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.subjectName

class Attendance(models.Model):
    attendanceDate = models.DateField(auto_now_add=True)
    attendanceTeacherId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_taker')
    attendanceCourseId = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='current_course')
    attendanceSubject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.attendanceDate)

class AttendanceStatus(models.Model):
    attendanceStatusName = models.CharField(max_length=255)
    attendanceStatusDesc = models.TextField(max_length=4000)

    def __str__(self):
        return self.attendanceStatusName

class DailyAttendance(models.Model):
    dailyAttendanceStudentStatus = models.ForeignKey(AttendanceStatus, on_delete=models.CASCADE,)
    dailyAttendanceStudentId = models.ForeignKey(User, on_delete=models.CASCADE,)
    dailyAttendanceAttendanceId = models.ForeignKey(Attendance, on_delete=models.CASCADE,)

    def __str__(self):
        return str(self.dailyAttendanceStudentId)

class Announcement(models.Model):
    announcementDate = models.DateField(auto_now_add=True)
    announcementPosterId = models.ForeignKey(User, on_delete=models.CASCADE,)
    announcementCourse = models.ForeignKey(Course, on_delete=models.CASCADE,)
    announcementFeed = models.TextField(max_length=4000)

    def __str__(self):
        return str(self.announcementPosterId)

class ResultType(models.Model):
    ResultTypeName = models.CharField(max_length=255)
    ResultTypeDesc = models.TextField(max_length=4000)

    def __str__(self):
        return self.ResultTypeName

class Result(models.Model):
    resultType = models.ForeignKey(ResultType, on_delete=models.CASCADE,)
    resultStudentId = models.ForeignKey(User, on_delete=models.CASCADE,)
    resultStudentMark = models.IntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)], null=True)
    resultFeedback = models.CharField(max_length=255, default="", blank=True, null=True)
    resultReturnedDate = models.DateField(auto_now_add=True)
    resultCourse = models.ForeignKey(Course, on_delete=models.CASCADE,)
    resultName = models.CharField(max_length=255)
    resultSubject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.resultStudentId)

class Material(models.Model):
    materialTitle = models.CharField(max_length=255)
    materialDescription = models.TextField(max_length=4000)
    materialCourse = models.ForeignKey(Course, on_delete=models.CASCADE,)
    materialSubject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    materialDocument = models.FileField(upload_to='documents/')
    materialUploadTime = models.DateTimeField(auto_now_add=True)
    materialPosterId = models.ForeignKey(User, on_delete=models.CASCADE,)

    def __str__(self):
        return str(self.materialTitle)

class Discussion(models.Model):
    discussionMaterial = models.ForeignKey(Material, on_delete=models.CASCADE,)
    discussionPost = models.TextField(max_length=4000)
    discussionCreatedTime = models.DateTimeField(auto_now_add=True)
    discussionUpdatedTime = models.DateTimeField(null=True)
    discussionPoster = models.ForeignKey(User, on_delete=models.CASCADE,)
    discussionCourse = models.ForeignKey(Course, on_delete=models.CASCADE,)

    def __str__(self):
        return str(self.discussionPost)

#class Event(models.Model):
#    title = models.CharField(max_length=200)
#    description = models.TextField()
#    start_time = models.DateTimeField()
#    end_time = models.DateTimeField()

#class Event(models.Model):
#    eventTitle = models.CharField(max_length=200)
#    eventDescription = models.TextField(max_length=4000)
#    eventTime = models.DateTimeField()
#    eventTimePosterId = models.ForeignKey(User, on_delete=models.CASCADE,)
#    eventCourse = models.ForeignKey(Course, on_delete=models.CASCADE,)
#    eventDatePosted = models.DateTimeField(auto_now_add=True)

#class AssigntmentDeadline(models.Model):
#    assigntmentDeadlineDatePosted = models.DateTimeField(auto_now_add=True)
#    assigntmentDeadlinePosterId = models.ForeignKey(User, on_delete=models.CASCADE,)
#    assigntmentDeadlineMemo = models.TextField(max_length=4000)
#    assigntmentDeadlineCourse = models.ForeignKey(Course, on_delete=models.CASCADE,)
#    assigntmentDeadlineTitle = models.CharField(max_length=255)
#    assigntmentDeadlineDueDate = models.DateTimeField(default=datetime.now())
#
#    def __str__(self):
#        return str(self.assigntmentDeadlineTitle)

#class ExamDate(models.Model):
#    examDateDatePosted = models.DateTimeField(auto_now_add=True)
#    examDatePosterId = models.ForeignKey(User, on_delete=models.CASCADE,)
#    examDateMemo = models.TextField(max_length=4000)
#    examDateCourse = models.ForeignKey(Course, on_delete=models.CASCADE,)
#    examDateTitle = models.CharField(max_length=255)
#    examDateDate = models.DateTimeField(default=datetime.now())
#
#    def __str__(self):
#        return str(self.calendarHeading)
