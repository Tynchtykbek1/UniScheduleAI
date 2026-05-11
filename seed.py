from datetime import time

from app import create_app
from models import (
    Course,
    Professor,
    Room,
    StudentProfile,
    Subject,
    TimetableSlot,
    User,
    db,
)


def parse_time(value):
    return time.fromisoformat(value)


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(username="admin", email="admin@example.com", role="admin")
    admin.set_password("admin123")

    student = User(username="student", email="student@example.com", role="student")
    student.set_password("student123")

    computer_science = Course(
        name="Computer Science",
        year=2,
        semester=1,
        student_count=75,
    )
    data_analytics = Course(
        name="Data Analytics",
        year=3,
        semester=1,
        student_count=35,
    )

    professors = {
        "rossi": Professor(name="Prof. Rossi", email="rossi@example.com"),
        "bianchi": Professor(name="Prof. Bianchi", email="bianchi@example.com"),
        "verdi": Professor(name="Prof. Verdi", email="verdi@example.com"),
        "conti": Professor(name="Prof. Conti", email="conti@example.com"),
    }

    rooms = {
        "room_a": Room(name="Room A", capacity=80),
        "room_b": Room(name="Room B", capacity=40),
        "lab_1": Room(name="Lab 1", capacity=30),
        "aula_magna": Room(name="Aula Magna", capacity=120),
    }

    db.session.add_all(
        [
            admin,
            student,
            computer_science,
            data_analytics,
            *professors.values(),
            *rooms.values(),
        ]
    )
    db.session.commit()

    student_profile = StudentProfile(
        user_id=student.id,
        course_id=computer_science.id,
    )

    computer_science_subjects = {
        "web_programming": Subject(
            name="Web Programming",
            course_id=computer_science.id,
        ),
        "operating_systems": Subject(
            name="Operating Systems",
            course_id=computer_science.id,
        ),
        "databases": Subject(
            name="Databases",
            course_id=computer_science.id,
        ),
        "artificial_intelligence": Subject(
            name="Artificial Intelligence",
            course_id=computer_science.id,
        ),
        "computer_networks": Subject(
            name="Computer Networks",
            course_id=computer_science.id,
        ),
    }

    data_analytics_subjects = {
        "data_mining": Subject(
            name="Data Mining",
            course_id=data_analytics.id,
        ),
        "statistics": Subject(
            name="Statistics",
            course_id=data_analytics.id,
        ),
        "machine_learning": Subject(
            name="Machine Learning",
            course_id=data_analytics.id,
        ),
        "data_visualization": Subject(
            name="Data Visualization",
            course_id=data_analytics.id,
        ),
        "big_data_systems": Subject(
            name="Big Data Systems",
            course_id=data_analytics.id,
        ),
    }

    db.session.add(student_profile)
    db.session.add_all(computer_science_subjects.values())
    db.session.add_all(data_analytics_subjects.values())
    db.session.commit()

    timetable_slots = [
        TimetableSlot(
            subject_id=computer_science_subjects["web_programming"].id,
            professor_id=professors["rossi"].id,
            room_id=rooms["room_a"].id,
            day="Monday",
            start_time=parse_time("09:00"),
            end_time=parse_time("11:00"),
        ),
        TimetableSlot(
            subject_id=computer_science_subjects["operating_systems"].id,
            professor_id=professors["bianchi"].id,
            room_id=rooms["room_a"].id,
            day="Monday",
            start_time=parse_time("11:00"),
            end_time=parse_time("13:00"),
        ),
        TimetableSlot(
            subject_id=computer_science_subjects["databases"].id,
            professor_id=professors["verdi"].id,
            room_id=rooms["room_a"].id,
            day="Tuesday",
            start_time=parse_time("09:00"),
            end_time=parse_time("11:00"),
        ),
        TimetableSlot(
            subject_id=computer_science_subjects["artificial_intelligence"].id,
            professor_id=professors["conti"].id,
            room_id=rooms["room_a"].id,
            day="Wednesday",
            start_time=parse_time("14:00"),
            end_time=parse_time("16:00"),
        ),
        TimetableSlot(
            subject_id=computer_science_subjects["computer_networks"].id,
            professor_id=professors["bianchi"].id,
            room_id=rooms["room_a"].id,
            day="Thursday",
            start_time=parse_time("09:00"),
            end_time=parse_time("11:00"),
        ),
        TimetableSlot(
            subject_id=computer_science_subjects["web_programming"].id,
            professor_id=professors["rossi"].id,
            room_id=rooms["lab_1"].id,
            day="Friday",
            start_time=parse_time("11:00"),
            end_time=parse_time("13:00"),
        ),
        TimetableSlot(
            subject_id=data_analytics_subjects["data_mining"].id,
            professor_id=professors["verdi"].id,
            room_id=rooms["room_b"].id,
            day="Monday",
            start_time=parse_time("14:00"),
            end_time=parse_time("16:00"),
        ),
        TimetableSlot(
            subject_id=data_analytics_subjects["statistics"].id,
            professor_id=professors["conti"].id,
            room_id=rooms["room_b"].id,
            day="Tuesday",
            start_time=parse_time("11:00"),
            end_time=parse_time("13:00"),
        ),
        TimetableSlot(
            subject_id=data_analytics_subjects["machine_learning"].id,
            professor_id=professors["rossi"].id,
            room_id=rooms["room_b"].id,
            day="Wednesday",
            start_time=parse_time("09:00"),
            end_time=parse_time("11:00"),
        ),
        TimetableSlot(
            subject_id=data_analytics_subjects["data_visualization"].id,
            professor_id=professors["bianchi"].id,
            room_id=rooms["room_b"].id,
            day="Thursday",
            start_time=parse_time("14:00"),
            end_time=parse_time("16:00"),
        ),
        TimetableSlot(
            subject_id=data_analytics_subjects["big_data_systems"].id,
            professor_id=professors["verdi"].id,
            room_id=rooms["room_b"].id,
            day="Friday",
            start_time=parse_time("09:00"),
            end_time=parse_time("11:00"),
        ),
    ]

    db.session.add_all(timetable_slots)
    db.session.commit()

    print("Database seeded successfully.")
    print("Admin login: admin / admin123")
    print("Student login: student / student123")
    print(f"Courses created: {Course.query.count()}")
    print(f"Subjects created: {Subject.query.count()}")
    print(f"Rooms created: {Room.query.count()}")
    print(f"Timetable slots created: {TimetableSlot.query.count()}")
