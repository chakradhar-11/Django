from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/attendance/', views.mark_attendance, name='mark_attendance'),
    path('teacher/marks/', views.enter_marks, name='enter_marks'),
    path('student/profile/', views.student_profile, name='student_profile'),
]
