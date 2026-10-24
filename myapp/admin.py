from django.contrib import admin
from .models import Student, Teacher, Course, StudentCourse, Attendance, Marks

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(StudentCourse)
admin.site.register(Attendance)
admin.site.register(Marks)