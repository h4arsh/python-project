"""
data_handler.py
----------------
All file-handling logic lives here, separate from the Flask routes.
This mirrors what your console app did (reading/writing a data file),
just swapped from plain text to JSON so it's easy to store multiple
subjects and marks per student.
"""

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def load_students():
    """Read all student records from the JSON file. Returns a list of dicts."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_students(students):
    """Write the full list of student records back to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=2)


def get_next_id(students):
    """Generate the next unique id (simple auto-increment)."""
    if not students:
        return 1
    return max(s["id"] for s in students) + 1


def find_student(students, student_id):
    """Look up a single student by id. Returns the dict or None."""
    for s in students:
        if s["id"] == student_id:
            return s
    return None


def calculate_result(subjects):
    """
    Given a dict like {"Math": 80, "Science": 75}, return
    total, percentage, and grade. This is the 'business logic'
    your console app had for computing results.
    """
    if not subjects:
        return {"total": 0, "percentage": 0.0, "grade": "N/A"}

    total = sum(subjects.values())
    percentage = round(total / len(subjects), 2)

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    elif percentage >= 40:
        grade = "E"
    else:
        grade = "F"

    return {"total": total, "percentage": percentage, "grade": grade}


def get_subject_averages(students):
    """
    Aggregate marks per subject across every student, so the dashboard
    chart reflects real data rather than placeholder numbers.
    Returns a list of {"subject": ..., "average": ...} sorted by subject name,
    which keeps the bar order stable across page loads.
    """
    totals = {}
    counts = {}
    for s in students:
        for subject, marks in s.get("subjects", {}).items():
            totals[subject] = totals.get(subject, 0) + marks
            counts[subject] = counts.get(subject, 0) + 1

    averages = [
        {"subject": subject, "average": round(totals[subject] / counts[subject], 1)}
        for subject in totals
    ]
    averages.sort(key=lambda x: x["subject"])
    return averages


def get_top_performers(students, limit=4):
    """Return the top N students by percentage, each with their result attached."""
    enriched = []
    for s in students:
        entry = dict(s)
        entry["result"] = calculate_result(s.get("subjects", {}))
        enriched.append(entry)
    enriched.sort(key=lambda x: x["result"]["percentage"], reverse=True)
    return enriched[:limit]
