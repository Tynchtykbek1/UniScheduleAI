from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import Course, DAYS_OF_WEEK, StudentProfile, Subject, TimetableSlot, db


user_bp = Blueprint("user", __name__)


def sort_slots_by_day_and_time(slots):
    day_order = {day: index for index, day in enumerate(DAYS_OF_WEEK)}
    return sorted(slots, key=lambda slot: (day_order.get(slot.day, 99), slot.start_time))


def get_student_timetable(user, day=None):
    # Reusable timetable lookup for student views and the future AI assistant.
    if not user.student_profile:
        return []

    query = TimetableSlot.query.join(Subject).filter(
        Subject.course_id == user.student_profile.course_id
    )

    if day in DAYS_OF_WEEK:
        query = query.filter(TimetableSlot.day == day)

    slots = query.all()
    return sort_slots_by_day_and_time(slots)


def format_timetable_for_ai(user):
    # Convert timetable slots into compact text suitable for an AI prompt later.
    slots = get_student_timetable(user)
    if not slots:
        return "No timetable data available."

    lines = []
    for slot in slots:
        start_time = slot.start_time.strftime("%H:%M")
        end_time = slot.end_time.strftime("%H:%M")
        lines.append(
            f"{slot.day} {start_time}-{end_time} | "
            f"{slot.subject.name} | Prof. {slot.professor.name} | {slot.room.name}"
        )

    return "\n".join(lines)


@user_bp.route("/")
def index():
    # Authenticated users skip the public landing page.
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.timetable"))

    return render_template("index.html")


@user_bp.route("/timetable")
@login_required
def timetable():
    # Admin users manage timetables from the admin dashboard.
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))

    profile = current_user.student_profile
    if not profile:
        flash(
            "Your student profile is missing. Please contact an administrator.",
            "warning",
        )
        return redirect(url_for("auth.logout"))

    selected_day = request.args.get("day")
    if selected_day and selected_day not in DAYS_OF_WEEK:
        flash("Invalid day filter ignored.", "warning")
        selected_day = None

    slots = get_student_timetable(current_user, selected_day)

    return render_template(
        "timetable.html",
        profile=profile,
        course=profile.course,
        slots=slots,
        days_of_week=DAYS_OF_WEEK,
        selected_day=selected_day,
    )


@user_bp.route("/profile")
@login_required
def profile():
    # Student profile is read-only here; admins use their own dashboard.
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))

    profile = current_user.student_profile
    course = profile.course if profile else None

    return render_template("profile.html", profile=profile, course=course)
