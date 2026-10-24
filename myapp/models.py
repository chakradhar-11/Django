
from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    course = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.name} - {self.date} - {status}"


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    marks_obtained = models.DecimalField(
        max_digits=6, decimal_places=2
    )
    total_marks = models.DecimalField(
        max_digits=6, decimal_places=2
    )

    class Meta:
        verbose_name = "Mark"
        verbose_name_plural = "Marks"

    def __str__(self):
        return f"{self.student.name} - {self.exam_name}"
