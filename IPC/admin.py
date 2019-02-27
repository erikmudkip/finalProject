from django.contrib import admin

from .models import Institution
from .models import Course
from .models import Subject
from .models import Attendance
from .models import DailyAttendance
from .models import AttendanceStatus
from .models import Announcement
from .models import ResultType
from .models import Result
from .models import AssigntmentDeadline
from .models import ExamDate


admin.site.register(Institution)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Attendance)
admin.site.register(DailyAttendance)
admin.site.register(AttendanceStatus)
admin.site.register(Announcement)
admin.site.register(ResultType)
admin.site.register(Result)
admin.site.register(AssigntmentDeadline)
admin.site.register(ExamDate)
