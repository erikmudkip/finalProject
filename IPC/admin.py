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
from .models import Material
from .models import Discussion
from .models import ForumTopic
from .models import ForumTopicPost
from .models import Event

admin.site.register(Institution)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Attendance)
admin.site.register(DailyAttendance)
admin.site.register(AttendanceStatus)
admin.site.register(Announcement)
admin.site.register(ResultType)
admin.site.register(Result)
admin.site.register(Material)
admin.site.register(Discussion)
admin.site.register(ForumTopic)
admin.site.register(ForumTopicPost)
admin.site.register(Event)
