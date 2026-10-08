"""
app.py
------
Flask application for the Student Result Management System.

Routes:
  GET  /                     -> list all students (Read)
  GET  /student/<id>         -> view one student's full result (Read)
  GET  /add                  -> show "add student" form
  POST /add                  -> create a new student (Create)
  GET  /edit/<id>            -> show "edit student" form pre-filled
  POST /edit/<id>            -> update an existing student (Update)
  POST /delete/<id>          -> delete a student (Delete)
  GET  /search                -> search by roll number
"""

from flask import Flask, render_template, request, redirect, url_for, flash

from data_handler import (
    load_students,
    save_students,
    get_next_id,
    find_student,
    calculate_result,
    get_subject_averages,
    get_top_performers,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # needed only for flash messages


@app.route("/")
def index():
    students = load_students()
    # attach computed result to each student so the template can show it
    for s in students:
        s["result"] = calculate_result(s["subjects"])

    subject_averages = get_subject_averages(students)
    top_performers = get_top_performers(students, limit=4)
    class_average = (
        round(sum(s["result"]["percentage"] for s in students) / len(students), 1)
        if students else 0
    )

    class_sections = build_class_sections(students)

    return render_template(
        "index.html",
        students=students,
        subject_averages=subject_averages,
        top_performers=top_performers,
        class_average=class_average,
        student_count=len(students),
        class_sections=class_sections,
        active_page="dashboard",
    )


CLASSES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


def build_class_sections(students):
    """Group students by class (1-10), each sorted by percentage (top to bottom)."""
    sections = []
    for cls in CLASSES:
        members = [s for s in students if str(s.get("student_class", "")) == cls]
        members.sort(key=lambda s: s["result"]["percentage"], reverse=True)
        avg = (
            round(sum(s["result"]["percentage"] for s in members) / len(members), 1)
            if members else 0
        )
        sections.append({
            "name": cls,
            "students": members,
            "count": len(members),
            "average": avg,
            "topper": members[0] if members else None,
        })
    return sections


@app.route("/class/<class_name>")
def class_dashboard(class_name):
    students = load_students()
    for s in students:
        s["result"] = calculate_result(s["subjects"])

    members = [s for s in students if str(s.get("student_class", "")) == class_name]
    members.sort(key=lambda s: s["result"]["percentage"], reverse=True)

    subject_averages = get_subject_averages(members)
    top_performers = get_top_performers(members, limit=4)
    class_average = (
        round(sum(s["result"]["percentage"] for s in members) / len(members), 1)
        if members else 0
    )

    return render_template(
        "class_dashboard.html",
        class_name=class_name,
        students=members,
        subject_averages=subject_averages,
        top_performers=top_performers,
        class_average=class_average,
        student_count=len(members),
        classes=CLASSES,
        active_page=f"class_{class_name}",
    )


@app.route("/student/<int:student_id>")
def view_student(student_id):
    students = load_students()
    student = find_student(students, student_id)
    if student is None:
        flash("Student not found.")
        return redirect(url_for("index"))
    result = calculate_result(student["subjects"])
    class_averages = get_subject_averages(students)
    return render_template(
        "view.html", student=student, result=result, class_averages=class_averages
    )


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        students = load_students()

        name = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()
        student_class = request.form.get("student_class", "").strip()

        # Subjects come in as parallel lists: subject_name[] and marks[]
        subject_names = request.form.getlist("subject_name")
        subject_marks = request.form.getlist("subject_marks")

        subjects = {}
        for sname, smark in zip(subject_names, subject_marks):
            sname = sname.strip()
            if sname and smark.strip():
                try:
                    subjects[sname] = int(smark)
                except ValueError:
                    pass

        if not name or not roll_no:
            flash("Name and roll number are required.")
            return redirect(url_for("add_student"))

        new_student = {
            "id": get_next_id(students),
            "name": name,
            "roll_no": roll_no,
            "student_class": student_class,
            "subjects": subjects,
        }
        students.append(new_student)
        save_students(students)
        flash(f"Student '{name}' added.")
        return redirect(url_for("index"))

    return render_template("add.html", active_page="add")


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    students = load_students()
    student = find_student(students, student_id)
    if student is None:
        flash("Student not found.")
        return redirect(url_for("index"))

    if request.method == "POST":
        student["name"] = request.form.get("name", "").strip()
        student["roll_no"] = request.form.get("roll_no", "").strip()
        student["student_class"] = request.form.get("student_class", "").strip()

        subject_names = request.form.getlist("subject_name")
        subject_marks = request.form.getlist("subject_marks")

        subjects = {}
        for sname, smark in zip(subject_names, subject_marks):
            sname = sname.strip()
            if sname and smark.strip():
                try:
                    subjects[sname] = int(smark)
                except ValueError:
                    pass
        student["subjects"] = subjects

        save_students(students)
        flash(f"Student '{student['name']}' updated.")
        return redirect(url_for("index"))

    return render_template("edit.html", student=student)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    students = load_students()
    student = find_student(students, student_id)
    if student is None:
        flash("Student not found.")
        return redirect(url_for("index"))

    students = [s for s in students if s["id"] != student_id]
    save_students(students)
    flash(f"Student '{student['name']}' deleted.")
    return redirect(url_for("index"))


@app.route("/search")
def search():
    query = request.args.get("q", "").strip().lower()
    all_students = load_students()
    students = all_students
    if query:
        students = [
            s for s in all_students
            if query in s["roll_no"].lower() or query in s["name"].lower()
        ]
    for s in students:
        s["result"] = calculate_result(s["subjects"])

    # dashboard stats always reflect the full class, not just search results
    for s in all_students:
        s["result"] = calculate_result(s["subjects"])
    subject_averages = get_subject_averages(all_students)
    top_performers = get_top_performers(all_students, limit=4)
    class_average = (
        round(sum(s["result"]["percentage"] for s in all_students) / len(all_students), 1)
        if all_students else 0
    )

    return render_template(
        "index.html",
        students=students,
        query=query,
        subject_averages=subject_averages,
        top_performers=top_performers,
        class_average=class_average,
        student_count=len(all_students),
        class_sections=build_class_sections(all_students),
    )


if __name__ == "__main__":
    app.run(debug=True)
