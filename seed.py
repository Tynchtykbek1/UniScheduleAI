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


ROOMS = {
    "A-T-1 (Campus Papardo)": 120,
    "A-S-1 (Campus Papardo)": 100,
    "A-T-10": 120,
    "SBA-T-1": 80,
    "SBA-T-3": 80,
    "324 (dept. Engineering)": 80,
    "316 (dept. of Engineering)": 80,
}

PROFESSORS = [
    "E. Barbera",
    "D. Costa",
    "G. Rinaldo",
    "Contract",
    "G. Finocchio",
    "D. Barilla",
    "L. Carnevale",
    "A. Celesti",
    "M. Villari",
    "A. Ruggeri",
    "G. Fiumara",
    "G. Consolo",
    "M. Gorgone",
    "M. Cutroneo",
    "S. Distefano",
    "M. Fazio",
    "C. Corsaro",
    "D. Ravì",
    "Not specified",
]

COURSES = [
    {"name": "Data Analysis", "year": 1, "semester": 1, "student_count": 80},
    {"name": "Data Analysis", "year": 2, "semester": 1, "student_count": 70},
    {"name": "Data Analysis", "year": 3, "semester": 1, "student_count": 45},
    {"name": "Data Analysis", "year": 1, "semester": 2, "student_count": 80},
    {"name": "Data Analysis", "year": 2, "semester": 2, "student_count": 70},
    {"name": "Data Analysis", "year": 3, "semester": 2, "student_count": 45},
]

TIMETABLE_DATA = {
    (1, 1): {
        "subjects": [
            "Calculus 1",
            "Physics 1",
            "Discrete Mathematics",
            "Programming",
        ],
        "slots": [
            ("Monday", "09:00", "11:00", "Calculus 1", "E. Barbera", "A-T-1 (Campus Papardo)"),
            ("Wednesday", "09:00", "11:00", "Calculus 1", "E. Barbera", "A-T-1 (Campus Papardo)"),
            ("Thursday", "09:00", "11:00", "Physics 1", "D. Costa", "A-T-1 (Campus Papardo)"),
            ("Monday", "11:00", "13:00", "Discrete Mathematics", "G. Rinaldo", "A-T-1 (Campus Papardo)"),
            ("Tuesday", "11:00", "13:00", "Physics 1", "D. Costa", "A-T-1 (Campus Papardo)"),
            ("Thursday", "11:00", "13:00", "Discrete Mathematics", "G. Rinaldo", "A-T-1 (Campus Papardo)"),
            ("Friday", "11:00", "13:00", "Physics 1", "D. Costa", "A-T-1 (Campus Papardo)"),
            ("Monday", "14:00", "16:00", "Discrete Mathematics", "G. Rinaldo", "A-T-1 (Campus Papardo)"),
            ("Tuesday", "14:00", "16:00", "Programming", "Contract", "A-T-1 (Campus Papardo)"),
            ("Wednesday", "14:00", "16:00", "Programming", "Contract", "A-T-1 (Campus Papardo)"),
            ("Thursday", "14:00", "16:00", "Calculus 1", "E. Barbera", "A-T-1 (Campus Papardo)"),
            ("Monday", "16:00", "18:00", "Programming", "Contract", "A-T-1 (Campus Papardo)"),
            ("Wednesday", "16:00", "18:00", "Programming", "Contract", "A-T-1 (Campus Papardo)"),
        ],
    },
    (2, 1): {
        "subjects": [
            "Devices and Circuits for Artificial Intelligence",
            "Statistical Methods and Models",
            "Computer Networks",
            "Operating Systems",
            "Database (module Database)",
        ],
        "slots": [
            ("Monday", "09:00", "11:00", "Devices and Circuits for Artificial Intelligence", "G. Finocchio", "A-S-1 (Campus Papardo)"),
            ("Tuesday", "09:00", "11:00", "Statistical Methods and Models", "D. Barilla", "A-S-1 (Campus Papardo)"),
            ("Wednesday", "09:00", "11:00", "Computer Networks", "L. Carnevale", "A-S-1 (Campus Papardo)"),
            ("Thursday", "09:00", "11:00", "Operating Systems", "Not specified", "A-S-1 (Campus Papardo)"),
            ("Friday", "09:00", "11:00", "Statistical Methods and Models", "D. Barilla", "A-S-1 (Campus Papardo)"),
            ("Monday", "11:00", "13:00", "Operating Systems", "Not specified", "A-S-1 (Campus Papardo)"),
            ("Tuesday", "11:00", "13:00", "Devices and Circuits for Artificial Intelligence", "G. Finocchio", "A-S-1 (Campus Papardo)"),
            ("Wednesday", "11:00", "13:00", "Operating Systems", "Not specified", "A-S-1 (Campus Papardo)"),
            ("Thursday", "11:00", "13:00", "Computer Networks", "L. Carnevale", "A-S-1 (Campus Papardo)"),
            ("Friday", "11:00", "13:00", "Computer Networks", "L. Carnevale", "A-S-1 (Campus Papardo)"),
            ("Monday", "14:00", "16:00", "Database (module Database)", "A. Celesti", "A-S-1 (Campus Papardo)"),
            ("Tuesday", "14:00", "16:00", "Database (module Database)", "A. Celesti", "A-S-1 (Campus Papardo)"),
            ("Thursday", "14:00", "16:00", "Database (module Database)", "A. Celesti", "A-S-1 (Campus Papardo)"),
        ],
    },
    (3, 1): {
        "subjects": [
            "System Security",
            "Web Programming",
            "Software Engineering",
            "Machine Learning",
        ],
        "slots": [
            ("Monday", "09:00", "11:00", "System Security", "M. Villari", "SBA-T-1"),
            ("Tuesday", "09:00", "11:00", "System Security", "M. Villari", "SBA-T-3"),
            ("Wednesday", "09:00", "11:00", "Web Programming", "A. Ruggeri", "SBA-T-3"),
            ("Monday", "11:00", "13:00", "System Security", "M. Villari", "SBA-T-1"),
            ("Tuesday", "11:00", "13:00", "Software Engineering", "Not specified", "SBA-T-1"),
            ("Wednesday", "11:00", "13:00", "Software Engineering", "Not specified", "SBA-T-3"),
            ("Monday", "14:00", "16:00", "Web Programming", "A. Ruggeri", "324 (dept. Engineering)"),
            ("Tuesday", "14:00", "16:00", "Web Programming", "A. Ruggeri", "324 (dept. Engineering)"),
            ("Wednesday", "14:00", "16:00", "Machine Learning", "G. Fiumara", "324 (dept. Engineering)"),
            ("Thursday", "14:00", "16:00", "Software Engineering", "Not specified", "324 (dept. Engineering)"),
            ("Monday", "16:00", "18:00", "Machine Learning", "G. Fiumara", "324 (dept. Engineering)"),
            ("Wednesday", "16:00", "18:00", "Machine Learning", "G. Fiumara", "324 (dept. Engineering)"),
            ("Thursday", "16:00", "18:00", "Web Programming", "A. Ruggeri", "324 (dept. Engineering)"),
        ],
    },
    (1, 2): {
        "subjects": [
            "Algorithms and Data Structures",
            "Mathematics for Data Analysis",
            "Physics 2",
            "Calculus 2",
        ],
        "slots": [
            ("Monday", "09:00", "11:00", "Algorithms and Data Structures", "G. Fiumara", "A-T-10"),
            ("Tuesday", "09:00", "11:00", "Algorithms and Data Structures", "G. Fiumara", "A-T-10"),
            ("Wednesday", "09:00", "11:00", "Mathematics for Data Analysis", "M. Gorgone", "A-T-10"),
            ("Thursday", "09:00", "11:00", "Physics 2", "M. Cutroneo", "A-T-10"),
            ("Monday", "11:00", "13:00", "Calculus 2", "G. Consolo", "A-T-10"),
            ("Tuesday", "11:00", "13:00", "Calculus 2", "G. Consolo", "A-T-10"),
            ("Wednesday", "11:00", "13:00", "Calculus 2", "G. Consolo", "A-T-10"),
            ("Thursday", "11:00", "13:00", "Algorithms and Data Structures", "G. Fiumara", "A-T-10"),
            ("Friday", "11:00", "13:00", "Physics 2", "M. Cutroneo", "A-T-10"),
            ("Monday", "14:00", "16:00", "Mathematics for Data Analysis", "M. Gorgone", "A-T-10"),
            ("Tuesday", "14:00", "16:00", "Mathematics for Data Analysis", "M. Gorgone", "A-T-10"),
            ("Wednesday", "14:00", "16:00", "Physics 2", "M. Cutroneo", "A-T-10"),
            ("Thursday", "14:00", "16:00", "Algorithms and Data Structures", "G. Fiumara", "A-T-10"),
            ("Monday", "16:00", "18:00", "Algorithms and Data Structures", "G. Fiumara", "A-T-10"),
        ],
    },
    (2, 2): {
        "subjects": [
            "Object Oriented Programming",
            "Operating Systems (mod. B)",
            "Database (mod. B)",
            "Device Physics",
        ],
        "slots": [
            ("Monday", "09:00", "11:00", "Object Oriented Programming", "S. Distefano", "A-S-1 (Campus Papardo)"),
            ("Tuesday", "09:00", "11:00", "Operating Systems (mod. B)", "M. Fazio", "A-S-1 (Campus Papardo)"),
            ("Wednesday", "09:00", "11:00", "Operating Systems (mod. B)", "M. Fazio", "A-S-1 (Campus Papardo)"),
            ("Thursday", "09:00", "11:00", "Database (mod. B)", "A. Ruggeri", "A-S-1 (Campus Papardo)"),
            ("Monday", "11:00", "13:00", "Operating Systems (mod. B)", "M. Fazio", "A-S-1 (Campus Papardo)"),
            ("Tuesday", "11:00", "13:00", "Object Oriented Programming", "S. Distefano", "A-S-1 (Campus Papardo)"),
            ("Wednesday", "11:00", "13:00", "Device Physics", "C. Corsaro", "A-S-1 (Campus Papardo)"),
            ("Thursday", "11:00", "13:00", "Database (mod. B)", "A. Ruggeri", "A-S-1 (Campus Papardo)"),
            ("Monday", "14:00", "16:00", "Database (mod. B)", "A. Ruggeri", "A-S-1 (Campus Papardo)"),
            ("Tuesday", "14:00", "16:00", "Object Oriented Programming", "S. Distefano", "A-S-1 (Campus Papardo)"),
            ("Wednesday", "14:00", "16:00", "Device Physics", "C. Corsaro", "A-S-1 (Campus Papardo)"),
            ("Thursday", "14:00", "16:00", "Device Physics", "C. Corsaro", "A-S-1 (Campus Papardo)"),
        ],
    },
    (3, 2): {
        "subjects": ["Data Mining"],
        "slots": [
            ("Tuesday", "11:00", "13:00", "Data Mining", "D. Ravì", "316 (dept. of Engineering)"),
            ("Wednesday", "11:00", "13:00", "Data Mining", "D. Ravì", "316 (dept. of Engineering)"),
            ("Thursday", "11:00", "13:00", "Data Mining", "D. Ravì", "316 (dept. of Engineering)"),
        ],
    },
}


def seed_users():
    admin = User(username="admin", email="admin@example.com", role="admin")
    admin.set_password("admin123")

    student = User(username="student", email="student@example.com", role="student")
    student.set_password("student123")

    db.session.add_all([admin, student])
    return student


def seed_courses():
    courses = {}
    for course_data in COURSES:
        course = Course(**course_data)
        db.session.add(course)
        courses[(course.year, course.semester)] = course
    return courses


def seed_rooms():
    rooms = {}
    for name, capacity in ROOMS.items():
        room = Room(name=name, capacity=capacity)
        db.session.add(room)
        rooms[name] = room
    return rooms


def seed_professors():
    professors = {}
    for name in PROFESSORS:
        professor = Professor(name=name)
        db.session.add(professor)
        professors[name] = professor
    return professors


def seed_subjects(courses):
    subjects = {}
    for course_key, data in TIMETABLE_DATA.items():
        for subject_name in data["subjects"]:
            subject = Subject(name=subject_name, course_id=courses[course_key].id)
            db.session.add(subject)
            subjects[(course_key, subject_name)] = subject
    return subjects


def seed_timetable_slots(subjects, professors, rooms):
    slots = []
    for course_key, data in TIMETABLE_DATA.items():
        for day, start, end, subject_name, professor_name, room_name in data["slots"]:
            slots.append(
                TimetableSlot(
                    subject_id=subjects[(course_key, subject_name)].id,
                    professor_id=professors[professor_name].id,
                    room_id=rooms[room_name].id,
                    day=day,
                    start_time=parse_time(start),
                    end_time=parse_time(end),
                )
            )
    db.session.add_all(slots)


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    student = seed_users()
    courses = seed_courses()
    rooms = seed_rooms()
    professors = seed_professors()
    db.session.commit()

    student_profile = StudentProfile(user_id=student.id, course_id=courses[(3, 1)].id)
    db.session.add(student_profile)

    subjects = seed_subjects(courses)
    db.session.commit()

    seed_timetable_slots(subjects, professors, rooms)
    db.session.commit()

    print("Database seeded successfully.")
    print("Admin login: admin / admin123")
    print("Student login: student / student123")
    print("Student linked to: Data Analysis, Year 3, Semester 1")
    print("Academic year: 2024-2025")
    print("Demo values: room capacities and student counts are demo values because the PDFs do not include them.")
    print(f"Courses created: {Course.query.count()}")
    print(f"Subjects created: {Subject.query.count()}")
    print(f"Rooms created: {Room.query.count()}")
    print(f"Professors created: {Professor.query.count()}")
    print(f"Timetable slots created: {TimetableSlot.query.count()}")
