from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def times_overlap(start1, end1, start2, end2):
    return start1 < end2 and start2 < end1


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship("StudentProfile", back_populates="user", uselist=False)
    chat_messages = db.relationship("AIChatMessage", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    student_count = db.Column(db.Integer, nullable=False, default=0)

    subjects = db.relationship("Subject", back_populates="course")
    student_profiles = db.relationship("StudentProfile", back_populates="course")

    def __repr__(self):
        return f"<Course {self.name}>"


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    course = db.relationship("Course", back_populates="subjects")
    timetable_slots = db.relationship("TimetableSlot", back_populates="subject")

    def __repr__(self):
        return f"<Subject {self.name}>"


class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=True)

    timetable_slots = db.relationship("TimetableSlot", back_populates="professor")

    def __repr__(self):
        return f"<Professor {self.name}>"


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    timetable_slots = db.relationship("TimetableSlot", back_populates="room")

    def __repr__(self):
        return f"<Room {self.name}>"


class TimetableSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey("professor.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    subject = db.relationship("Subject", back_populates="timetable_slots")
    professor = db.relationship("Professor", back_populates="timetable_slots")
    room = db.relationship("Room", back_populates="timetable_slots")

    @property
    def course(self):
        return self.subject.course

    def __repr__(self):
        return f"<TimetableSlot {self.day} {self.start_time}-{self.end_time}>"


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    user = db.relationship("User", back_populates="student_profile")
    course = db.relationship("Course", back_populates="student_profiles")

    def __repr__(self):
        return f"<StudentProfile user_id={self.user_id} course_id={self.course_id}>"


class AIChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="chat_messages")

    def __repr__(self):
        return f"<AIChatMessage user_id={self.user_id} created_at={self.created_at}>"
