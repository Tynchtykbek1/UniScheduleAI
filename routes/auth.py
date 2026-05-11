from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from models import Course, StudentProfile, User, db


auth_bp = Blueprint("auth", __name__)


def redirect_authenticated_user():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("user.timetable"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Authenticated users should not register again; send them to their future dashboard.
    if current_user.is_authenticated:
        return redirect_authenticated_user()

    courses = Course.query.all()

    # GET requests show the registration form with available courses.
    if request.method == "GET":
        return render_template("register.html", courses=courses)

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    course_id = request.form.get("course_id")

    # Validate required registration fields before touching the database.
    if not username or not email or not password or not confirm_password or not course_id:
        flash("All fields are required.", "danger")
        return render_template("register.html", courses=courses)

    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return render_template("register.html", courses=courses)

    if User.query.filter_by(username=username).first():
        flash("Username is already taken.", "danger")
        return render_template("register.html", courses=courses)

    if User.query.filter_by(email=email).first():
        flash("Email is already registered.", "danger")
        return render_template("register.html", courses=courses)

    course = Course.query.get(course_id)
    if not course:
        flash("Selected course does not exist.", "danger")
        return render_template("register.html", courses=courses)

    user = User(username=username, email=email, role="student")
    user.set_password(password)

    # Create the user first, then attach the required student profile.
    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Registration failed. Please try again.", "danger")
        return render_template("register.html", courses=courses)

    try:
        profile = StudentProfile(user_id=user.id, course_id=course.id)
        db.session.add(profile)
        db.session.commit()
    except Exception:
        db.session.rollback()
        db.session.delete(user)
        db.session.commit()
        flash("Registration failed while creating your student profile.", "danger")
        return render_template("register.html", courses=courses)

    flash("Registration successful. Please log in.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Logged-in users go directly to the future dashboard for their role.
    if current_user.is_authenticated:
        return redirect_authenticated_user()

    # GET requests show the login form.
    if request.method == "GET":
        return render_template("login.html")

    username_or_email = request.form.get("username_or_email")
    password = request.form.get("password")

    if not username_or_email or not password:
        flash("Invalid username/email or password.", "danger")
        return render_template("login.html")

    # Look up by either username or email, then verify the stored password hash.
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if user and user.check_password(password):
        login_user(user)
        flash("Login successful.", "success")

        if user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.timetable"))

    flash("Invalid username/email or password.", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    # End the current session and send the user back to the login page.
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
