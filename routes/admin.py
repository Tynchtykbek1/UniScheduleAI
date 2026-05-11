from datetime import time
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import (
    DAYS_OF_WEEK,
    Course,
    Professor,
    Room,
    Subject,
    TimetableSlot,
    User,
    db,
    times_overlap,
)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        # Only authenticated admins can access admin routes.
        if not current_user.is_authenticated:
            flash("Please log in to access the admin area.", "warning")
            return redirect(url_for("auth.login"))

        if current_user.role != "admin" and not current_user.is_admin:
            flash("You do not have permission to access the admin area.", "danger")
            return redirect(url_for("user.timetable"))

        return view_func(*args, **kwargs)

    return wrapped_view


def parse_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        flash(f"{field_name} must be a valid integer.", "danger")
        return None


def parse_form_time(value, field_name):
    try:
        return time.fromisoformat(value)
    except (TypeError, ValueError):
        flash(f"{field_name} must be a valid time in HH:MM format.", "danger")
        return None


def validate_timetable_slot(
    subject, professor, room, day, start_time, end_time, exclude_slot_id=None
):
    # A room must be large enough for the subject's course.
    if subject.course.student_count > room.capacity:
        return "Room capacity is insufficient for this course."

    slots_query = TimetableSlot.query.filter_by(day=day)
    if exclude_slot_id is not None:
        slots_query = slots_query.filter(TimetableSlot.id != exclude_slot_id)

    for slot in slots_query.all():
        overlaps = times_overlap(start_time, end_time, slot.start_time, slot.end_time)
        if not overlaps:
            continue

        if slot.room_id == room.id:
            return "This room is already booked at this time."

        if slot.professor_id == professor.id:
            return "This professor already has a class at this time."

        if slot.subject.course_id == subject.course_id:
            return "This course already has a class at this time."

    return None


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    # Dashboard shows high-level totals for the admin overview.
    counts = {
        "courses": Course.query.count(),
        "subjects": Subject.query.count(),
        "professors": Professor.query.count(),
        "rooms": Room.query.count(),
        "timetable_slots": TimetableSlot.query.count(),
        "users": User.query.count(),
    }
    return render_template("admin/dashboard.html", counts=counts)


@admin_bp.route("/courses")
@login_required
@admin_required
def courses():
    # List courses in a predictable order for admin management.
    courses_list = Course.query.order_by(Course.name, Course.year, Course.semester).all()
    return render_template("admin/courses.html", courses=courses_list)


@admin_bp.route("/courses/add", methods=["POST"])
@login_required
@admin_required
def add_course():
    name = request.form.get("name")
    year = parse_int(request.form.get("year"), "Year")
    semester = parse_int(request.form.get("semester"), "Semester")
    student_count = parse_int(request.form.get("student_count"), "Student count")

    if not name or year is None or semester is None or student_count is None:
        flash("All course fields are required.", "danger")
        return redirect(url_for("admin.courses"))

    course = Course(
        name=name,
        year=year,
        semester=semester,
        student_count=student_count,
    )
    db.session.add(course)
    db.session.commit()
    flash("Course added successfully.", "success")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/courses/edit/<int:id>", methods=["POST"])
@login_required
@admin_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    name = request.form.get("name")
    year = parse_int(request.form.get("year"), "Year")
    semester = parse_int(request.form.get("semester"), "Semester")
    student_count = parse_int(request.form.get("student_count"), "Student count")

    if not name or year is None or semester is None or student_count is None:
        flash("All course fields are required.", "danger")
        return redirect(url_for("admin.courses"))

    course.name = name
    course.year = year
    course.semester = semester
    course.student_count = student_count
    db.session.commit()
    flash("Course updated successfully.", "success")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/courses/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_course(id):
    course = Course.query.get_or_404(id)

    # Courses in use by subjects or student profiles cannot be deleted safely.
    if course.subjects or course.student_profiles:
        flash("Cannot delete a course that has subjects or students.", "warning")
        return redirect(url_for("admin.courses"))

    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully.", "success")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/subjects")
@login_required
@admin_required
def subjects():
    subjects_list = Subject.query.order_by(Subject.name).all()
    courses_list = Course.query.order_by(Course.name, Course.year, Course.semester).all()
    return render_template(
        "admin/subjects.html", subjects=subjects_list, courses=courses_list
    )


@admin_bp.route("/subjects/add", methods=["POST"])
@login_required
@admin_required
def add_subject():
    name = request.form.get("name")
    course_id = parse_int(request.form.get("course_id"), "Course")

    if not name or course_id is None:
        flash("Subject name and course are required.", "danger")
        return redirect(url_for("admin.subjects"))

    course = Course.query.get(course_id)
    if not course:
        flash("Selected course does not exist.", "danger")
        return redirect(url_for("admin.subjects"))

    subject = Subject(name=name, course_id=course.id)
    db.session.add(subject)
    db.session.commit()
    flash("Subject added successfully.", "success")
    return redirect(url_for("admin.subjects"))


@admin_bp.route("/subjects/edit/<int:id>", methods=["POST"])
@login_required
@admin_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    name = request.form.get("name")
    course_id = parse_int(request.form.get("course_id"), "Course")

    if not name or course_id is None:
        flash("Subject name and course are required.", "danger")
        return redirect(url_for("admin.subjects"))

    course = Course.query.get(course_id)
    if not course:
        flash("Selected course does not exist.", "danger")
        return redirect(url_for("admin.subjects"))

    subject.name = name
    subject.course_id = course.id
    db.session.commit()
    flash("Subject updated successfully.", "success")
    return redirect(url_for("admin.subjects"))


@admin_bp.route("/subjects/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)

    if subject.timetable_slots:
        flash("Cannot delete a subject that has timetable slots.", "warning")
        return redirect(url_for("admin.subjects"))

    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully.", "success")
    return redirect(url_for("admin.subjects"))


@admin_bp.route("/professors")
@login_required
@admin_required
def professors():
    professors_list = Professor.query.order_by(Professor.name).all()
    return render_template("admin/professors.html", professors=professors_list)


@admin_bp.route("/professors/add", methods=["POST"])
@login_required
@admin_required
def add_professor():
    name = request.form.get("name")
    email = request.form.get("email")

    if not name:
        flash("Professor name is required.", "danger")
        return redirect(url_for("admin.professors"))

    professor = Professor(name=name, email=email)
    db.session.add(professor)
    db.session.commit()
    flash("Professor added successfully.", "success")
    return redirect(url_for("admin.professors"))


@admin_bp.route("/professors/edit/<int:id>", methods=["POST"])
@login_required
@admin_required
def edit_professor(id):
    professor = Professor.query.get_or_404(id)
    name = request.form.get("name")
    email = request.form.get("email")

    if not name:
        flash("Professor name is required.", "danger")
        return redirect(url_for("admin.professors"))

    professor.name = name
    professor.email = email
    db.session.commit()
    flash("Professor updated successfully.", "success")
    return redirect(url_for("admin.professors"))


@admin_bp.route("/professors/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_professor(id):
    professor = Professor.query.get_or_404(id)

    if professor.timetable_slots:
        flash("Cannot delete a professor that has timetable slots.", "warning")
        return redirect(url_for("admin.professors"))

    db.session.delete(professor)
    db.session.commit()
    flash("Professor deleted successfully.", "success")
    return redirect(url_for("admin.professors"))


@admin_bp.route("/rooms")
@login_required
@admin_required
def rooms():
    rooms_list = Room.query.order_by(Room.name).all()
    return render_template("admin/rooms.html", rooms=rooms_list)


@admin_bp.route("/rooms/add", methods=["POST"])
@login_required
@admin_required
def add_room():
    name = request.form.get("name")
    capacity = parse_int(request.form.get("capacity"), "Capacity")

    if not name or capacity is None:
        flash("Room name and capacity are required.", "danger")
        return redirect(url_for("admin.rooms"))

    room = Room(name=name, capacity=capacity)
    db.session.add(room)
    db.session.commit()
    flash("Room added successfully.", "success")
    return redirect(url_for("admin.rooms"))


@admin_bp.route("/rooms/edit/<int:id>", methods=["POST"])
@login_required
@admin_required
def edit_room(id):
    room = Room.query.get_or_404(id)
    name = request.form.get("name")
    capacity = parse_int(request.form.get("capacity"), "Capacity")

    if not name or capacity is None:
        flash("Room name and capacity are required.", "danger")
        return redirect(url_for("admin.rooms"))

    room.name = name
    room.capacity = capacity
    db.session.commit()
    flash("Room updated successfully.", "success")
    return redirect(url_for("admin.rooms"))


@admin_bp.route("/rooms/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_room(id):
    room = Room.query.get_or_404(id)

    if room.timetable_slots:
        flash("Cannot delete a room that has timetable slots.", "warning")
        return redirect(url_for("admin.rooms"))

    db.session.delete(room)
    db.session.commit()
    flash("Room deleted successfully.", "success")
    return redirect(url_for("admin.rooms"))


@admin_bp.route("/timetable")
@login_required
@admin_required
def timetable():
    slots = TimetableSlot.query.order_by(
        TimetableSlot.day, TimetableSlot.start_time
    ).all()
    subjects_list = Subject.query.order_by(Subject.name).all()
    professors_list = Professor.query.order_by(Professor.name).all()
    rooms_list = Room.query.order_by(Room.name).all()
    return render_template(
        "admin/timetable.html",
        slots=slots,
        subjects=subjects_list,
        professors=professors_list,
        rooms=rooms_list,
        days_of_week=DAYS_OF_WEEK,
    )


def get_timetable_form_data():
    subject_id = parse_int(request.form.get("subject_id"), "Subject")
    professor_id = parse_int(request.form.get("professor_id"), "Professor")
    room_id = parse_int(request.form.get("room_id"), "Room")
    day = request.form.get("day")
    start_time = parse_form_time(request.form.get("start_time"), "Start time")
    end_time = parse_form_time(request.form.get("end_time"), "End time")

    if (
        subject_id is None
        or professor_id is None
        or room_id is None
        or start_time is None
        or end_time is None
    ):
        return None

    if day not in DAYS_OF_WEEK:
        flash("Selected day is invalid.", "danger")
        return None

    if start_time >= end_time:
        flash("Start time must be before end time.", "danger")
        return None

    subject = Subject.query.get(subject_id)
    professor = Professor.query.get(professor_id)
    room = Room.query.get(room_id)

    if not subject or not professor or not room:
        flash("Selected subject, professor, or room does not exist.", "danger")
        return None

    return subject, professor, room, day, start_time, end_time


@admin_bp.route("/timetable/add", methods=["POST"])
@login_required
@admin_required
def add_timetable_slot():
    form_data = get_timetable_form_data()
    if form_data is None:
        return redirect(url_for("admin.timetable"))

    subject, professor, room, day, start_time, end_time = form_data
    conflict = validate_timetable_slot(
        subject, professor, room, day, start_time, end_time
    )
    if conflict:
        flash(conflict, "warning")
        return redirect(url_for("admin.timetable"))

    slot = TimetableSlot(
        subject_id=subject.id,
        professor_id=professor.id,
        room_id=room.id,
        day=day,
        start_time=start_time,
        end_time=end_time,
    )
    db.session.add(slot)
    db.session.commit()
    flash("Timetable slot added successfully.", "success")
    return redirect(url_for("admin.timetable"))


@admin_bp.route("/timetable/edit/<int:id>", methods=["POST"])
@login_required
@admin_required
def edit_timetable_slot(id):
    slot = TimetableSlot.query.get_or_404(id)
    form_data = get_timetable_form_data()
    if form_data is None:
        return redirect(url_for("admin.timetable"))

    subject, professor, room, day, start_time, end_time = form_data
    conflict = validate_timetable_slot(
        subject, professor, room, day, start_time, end_time, exclude_slot_id=id
    )
    if conflict:
        flash(conflict, "warning")
        return redirect(url_for("admin.timetable"))

    slot.subject_id = subject.id
    slot.professor_id = professor.id
    slot.room_id = room.id
    slot.day = day
    slot.start_time = start_time
    slot.end_time = end_time
    db.session.commit()
    flash("Timetable slot updated successfully.", "success")
    return redirect(url_for("admin.timetable"))


@admin_bp.route("/timetable/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_timetable_slot(id):
    slot = TimetableSlot.query.get_or_404(id)
    db.session.delete(slot)
    db.session.commit()
    flash("Timetable slot deleted successfully.", "success")
    return redirect(url_for("admin.timetable"))


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users_list)
