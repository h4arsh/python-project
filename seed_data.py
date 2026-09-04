"""
seed_data.py
------------
Populate data.json with 10 sample students for each class (1-5).
Run once:  python seed_data.py
"""

import random

from data_handler import load_students, save_students, get_next_id

SUBJECTS = ["Math", "Science", "English", "Social Studies", "Computer"]

FIRST_NAMES = [
    "Aarav", "Ananya", "Arjun", "Diya", "Ishaan", "Kavya", "Krishna", "Meera",
    "Nikhil", "Priya", "Rahul", "Riya", "Rohan", "Sanya", "Vikram", "Zara",
    "Aditi", "Dev", "Farhan", "Gauri", "Harsh", "Ira", "Kabir", "Lakshmi",
    "Manav", "Neha", "Om", "Pooja", "Rehan", "Sneha",
]

LAST_NAMES = [
    "Sharma", "Patel", "Khan", "Gupta", "Singh", "Mehta", "Reddy", "Iyer",
    "Das", "Nair", "Verma", "Joshi", "Chopra", "Malhotra", "Bose",
]


def make_student(student_id, class_num, index):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    roll_no = f"C{class_num}-{index + 1:02d}"
    subjects = {sub: random.randint(35, 100) for sub in SUBJECTS}
    return {
        "id": student_id,
        "name": name,
        "roll_no": roll_no,
        "student_class": str(class_num),
        "subjects": subjects,
    }


def main():
    random.seed(42)
    students = load_students()
    next_id = get_next_id(students)

    for class_num in range(1, 6):
        for i in range(10):
            students.append(make_student(next_id, class_num, i))
            next_id += 1

    save_students(students)
    print(f"Seeded 50 students (10 per class, classes 1-5). Total now: {len(students)}")


if __name__ == "__main__":
    main()
