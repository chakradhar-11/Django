from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Student, Teacher, Course, StudentCourse, Attendance, Marks


def is_teacher(user):
    return user.is_authenticated and user.groups.filter(name="Teacher").exists()


def is_student(user):
    return user.is_authenticated and user.groups.filter(name="Student").exists()


def home(request):
    # The record-management home page is intended for the administrator.
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.is_superuser or request.user.is_staff:
        students = Student.objects.all().order_by("name")
        return render(request, "home.html", {"students": students})
    return redirect("dashboard")


@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff, login_url="dashboard")
def add_student(request):
    if request.method != "POST":
        return redirect("home")
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    course_name = request.POST.get("course", "").strip()
    phone = request.POST.get("phone", "").strip()
    if not all([name, email, course_name, phone]):
        messages.error(request, "Please fill in all fields.")
    elif Student.objects.filter(email=email).exists():
        messages.error(request, "This email is already registered.")
    else:
        Student.objects.create(name=name, email=email, course=course_name, phone=phone)
        messages.success(request, "Student added successfully!")
    return redirect("home")


@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff, login_url="dashboard")
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        course_name = request.POST.get("course", "").strip()
        phone = request.POST.get("phone", "").strip()
        if not all([name, email, course_name, phone]):
            messages.error(request, "Please fill in all fields.")
        elif Student.objects.filter(email=email).exclude(id=student_id).exists():
            messages.error(request, "This email is already registered.")
        else:
            student.name, student.email, student.course, student.phone = name, email, course_name, phone
            student.save()
            messages.success(request, "Student updated successfully!")
            return redirect("home")
    return render(request, "edit_student.html", {"student": student})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff, login_url="dashboard")
@require_POST
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect("home")



def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect("home")
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(request, "Invalid username or password.")

        elif user.is_superuser or user.is_staff:
            login(request, user)
            return redirect("home")

        elif user.groups.filter(name="Teacher").exists():
            login(request, user)
            return redirect("dashboard")

        elif user.groups.filter(name="Student").exists():
            login(request, user)
            return redirect("dashboard")

        else:
            messages.error(
                request,
                "No role assigned. Contact the administrator."
            )

    return render(request, "login.html")



@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser or user.is_staff:
        return redirect("home")
    if is_teacher(user):
        return render(request, "teacher_dashboard.html")
    if is_student(user):
        return render(request, "student_dashboard.html")
    messages.error(request, "No dashboard role assigned to this account.")
    logout(request)
    return redirect("login")


def assigned_students_for(teacher):
    return Student.objects.filter(studentcourse__course__teacher=teacher).distinct().order_by("name")


@login_required
@user_passes_test(is_teacher, login_url="dashboard")
def teacher_students(request):
    teacher = Teacher.objects.filter(user=request.user).first()
    students = assigned_students_for(teacher) if teacher else Student.objects.none()
    return render(request, "teacher_students.html", {"students": students})


@login_required
@user_passes_test(is_teacher, login_url="dashboard")
def mark_attendance(request):
    teacher = Teacher.objects.filter(user=request.user).first()
    courses = Course.objects.filter(teacher=teacher).order_by("name") if teacher else Course.objects.none()
    students = assigned_students_for(teacher) if teacher else Student.objects.none()
    if request.method == "POST":
        student = get_object_or_404(students, pk=request.POST.get("student"))
        course = get_object_or_404(courses, pk=request.POST.get("course"))
        date_text = request.POST.get("date", "")
        status = request.POST.get("status", "")
        try:
            attendance_date = date.fromisoformat(date_text)
        except ValueError:
            messages.error(request, "Please select a valid date.")
        else:
            if status not in ("present", "absent"):
                messages.error(request, "Please choose Present or Absent.")
            else:
                Attendance.objects.update_or_create(
                    student=student, course=course, date=attendance_date,
                    defaults={"is_present": status == "present"})
                messages.success(request, "Attendance saved successfully!")
                return redirect("mark_attendance")
    return render(request, "mark_attendance.html", {"students": students, "courses": courses, "today": date.today()})


@login_required
@user_passes_test(is_teacher, login_url="dashboard")
def enter_marks(request):
    teacher = Teacher.objects.filter(user=request.user).first()
    courses = Course.objects.filter(teacher=teacher).order_by("name") if teacher else Course.objects.none()
    students = assigned_students_for(teacher) if teacher else Student.objects.none()
    if request.method == "POST":
        student = get_object_or_404(students, pk=request.POST.get("student"))
        course = get_object_or_404(courses, pk=request.POST.get("course"))
        exam_name = request.POST.get("exam_name", "").strip()
        try:
            obtained = Decimal(request.POST.get("marks_obtained", ""))
            total = Decimal(request.POST.get("total_marks", ""))
            if not exam_name or total <= 0 or obtained < 0 or obtained > total:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            messages.error(request, "Enter a valid exam name and marks (obtained must not exceed total).")
        else:
            Marks.objects.create(student=student, course=course, exam_name=exam_name, marks_obtained=obtained, total_marks=total)
            messages.success(request, "Marks saved successfully!")
            return redirect("enter_marks")
    return render(request, "enter_marks.html", {"students": students, "courses": courses})


@login_required
@user_passes_test(is_student, login_url="dashboard")
def student_profile(request):
    # Student accounts are matched to a Student record by the account email.
    student = Student.objects.filter(email__iexact=request.user.email).first()
    if not student:
        messages.warning(request, "No student record matches your login email. Ask the administrator to use the same email address.")
    enrollments = StudentCourse.objects.filter(student=student).select_related("course") if student else StudentCourse.objects.none()
    attendance = Attendance.objects.filter(student=student).select_related("course").order_by("-date") if student else Attendance.objects.none()
    marks = Marks.objects.filter(student=student).select_related("course").order_by("course__name", "exam_name") if student else Marks.objects.none()
    return render(request, "student_profile.html", {"student": student, "enrollments": enrollments, "attendance_records": attendance, "marks_records": marks})
