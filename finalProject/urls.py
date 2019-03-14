"""finalProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as accounts_views
from IPC import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('course', views.course, name='course'),
    path('signup/', accounts_views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('<int:course_id>/statistic', views.course_statistic, name='course_statistic'),
    path('<int:course_id>/announcement', views.course_announcement, name='course_announcement'),
    path('<int:course_id>/announcement/createAnnouncement', views.create_course_announcement, name='create_course_announcement'),
    path('<int:course_id>/attendance', views.course_attendance, name='course_attendance'),
    path('<int:course_id>/attendance/createAttendance', views.create_course_attendance, name='create_course_attendance'),
    path('<int:course_id>/attendance/<int:attendance_id>/detail', views.course_attendance_detail, name='course_attendance_detail'),
    path('<int:course_id>/result', views.course_result, name='course_result'),
    path('<int:course_id>/result/<int:result_id>/detail', views.course_result_detail, name='course_result_detail'),
    path('<int:course_id>/result/postResult', views.post_course_result, name='post_course_result'),
    path('<int:course_id>/material', views.course_material, name='course_material'),
    path('<int:course_id>/material/postMaterial', views.post_course_material, name='post_course_material'),
    path('<int:course_id>/material/<int:material_id>', views.material_discussion, name='material_discussion'),
    path('<int:course_id>/material/<int:material_id>/createDiscussion', views.post_material_discussion, name='post_material_discussion'),
    path('<int:course_id>/material/<int:material_id>/editDiscussion/<int:discussion_id>', views.edit_material_discussion, name='edit_material_discussion'),
    #path('<int:course_id>/calendar', views.CalendarView.as_view(), name='calendar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
