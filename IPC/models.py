from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime

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

class Attendance(models.Model):
    attendanceDate = models.DateTimeField(auto_now_add=True)
    attendanceTeacherId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_taker')
    attendanceCourseId = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='current_course')

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
    announcementDate = models.DateTimeField(auto_now_add=True)
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
    resultStudentMark = models.IntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)])
    resultFeedback = models.CharField(max_length=255, default="")
    resultReturnedDate = models.DateTimeField(auto_now_add=True)
    resultCourse = models.ForeignKey(Course, on_delete=models.CASCADE,)
    resultName = models.CharField(max_length=255)


    def __str__(self):
        return str(self.resultStudentId)
