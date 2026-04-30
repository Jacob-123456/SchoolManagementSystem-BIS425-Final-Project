from tkinter import *
import sqlite3

# ---------------- FUNCTIONS ----------------

def add_student():
    sid = student_id_entry.get()
    name = student_name_entry.get()

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("INSERT OR REPLACE INTO students VALUES (?, ?)", (sid, name))

    conn.commit()
    conn.close()

    output.insert(END, "Student added")


def add_subject():
    sid = subject_id_entry.get()
    name = subject_name_entry.get()

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("INSERT OR REPLACE INTO subjects VALUES (?, ?)", (sid, name))

    conn.commit()
    conn.close()

    output.insert(END, "Subject added")


def add_assignment():
    aid = assignment_id_entry.get()
    sid = assignment_subject_entry.get()
    title = assignment_title_entry.get()

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("INSERT OR REPLACE INTO assignments VALUES (?, ?, ?)", (aid, sid, title))

    conn.commit()
    conn.close()

    output.insert(END, "Assignment added")


def add_result():
    student_id = result_student_entry.get()
    assignment_id = result_assignment_entry.get()

    try:
        score = float(result_score_entry.get())
    except:
        output.insert(END, "Invalid score")
        return

    if score >= 90:
        letter = "A"
    elif score >= 80:
        letter = "B"
    elif score >= 70:
        letter = "C"
    elif score >= 60:
        letter = "D"
    else:
        letter = "F"

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO results (student_id, assignment_id, score, letter) VALUES (?, ?, ?, ?)",
        (student_id, assignment_id, score, letter)
    )

    conn.commit()
    conn.close()

    output.insert(END, "Result added")


def search_student():
    name = search_entry.get()

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    query = """
    SELECT students.name, subjects.name, assignments.title, results.score, results.letter
    FROM students
    JOIN results ON students.student_id = results.student_id
    JOIN assignments ON assignments.assignment_id = results.assignment_id
    JOIN subjects ON subjects.subject_id = assignments.subject_id
    WHERE students.name LIKE ?
    """

    cursor.execute(query, ('%' + name + '%',))
    rows = cursor.fetchall()

    output.delete(0, END)

    if rows:
        for row in rows:
            output.insert(END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]} ({row[4]})")
    else:
        output.insert(END, "No results found")

    conn.close()


# ---------------- GUI ----------------

root = Tk()
root.title("School Management System")
root.geometry("700x600")

# Student
student_frame = LabelFrame(root, text="Student", padx=10, pady=10)
student_frame.pack(fill="x", padx=10, pady=5)

Label(student_frame, text="Student ID").grid(row=0, column=0)
student_id_entry = Entry(student_frame)
student_id_entry.grid(row=0, column=1)

Label(student_frame, text="Student Name").grid(row=1, column=0)
student_name_entry = Entry(student_frame)
student_name_entry.grid(row=1, column=1)

Button(student_frame, text="Add Student", command=add_student).grid(row=2, column=0, columnspan=2)

# Subject
subject_frame = LabelFrame(root, text="Subject", padx=10, pady=10)
subject_frame.pack(fill="x", padx=10, pady=5)

Label(subject_frame, text="Subject ID").grid(row=0, column=0)
subject_id_entry = Entry(subject_frame)
subject_id_entry.grid(row=0, column=1)

Label(subject_frame, text="Subject Name").grid(row=1, column=0)
subject_name_entry = Entry(subject_frame)
subject_name_entry.grid(row=1, column=1)

Button(subject_frame, text="Add Subject", command=add_subject).grid(row=2, column=0, columnspan=2)

# Assignment
assignment_frame = LabelFrame(root, text="Assignment", padx=10, pady=10)
assignment_frame.pack(fill="x", padx=10, pady=5)

Label(assignment_frame, text="Assignment ID").grid(row=0, column=0)
assignment_id_entry = Entry(assignment_frame)
assignment_id_entry.grid(row=0, column=1)

Label(assignment_frame, text="Subject ID").grid(row=1, column=0)
assignment_subject_entry = Entry(assignment_frame)
assignment_subject_entry.grid(row=1, column=1)

Label(assignment_frame, text="Title").grid(row=2, column=0)
assignment_title_entry = Entry(assignment_frame)
assignment_title_entry.grid(row=2, column=1)

Button(assignment_frame, text="Add Assignment", command=add_assignment).grid(row=3, column=0, columnspan=2)

# Result
result_frame = LabelFrame(root, text="Result", padx=10, pady=10)
result_frame.pack(fill="x", padx=10, pady=5)

Label(result_frame, text="Student ID").grid(row=0, column=0)
result_student_entry = Entry(result_frame)
result_student_entry.grid(row=0, column=1)

Label(result_frame, text="Assignment ID").grid(row=1, column=0)
result_assignment_entry = Entry(result_frame)
result_assignment_entry.grid(row=1, column=1)

Label(result_frame, text="Score").grid(row=2, column=0)
result_score_entry = Entry(result_frame)
result_score_entry.grid(row=2, column=1)

Button(result_frame, text="Add Result", command=add_result).grid(row=3, column=0, columnspan=2)

# Search
search_frame = LabelFrame(root, text="Search", padx=10, pady=10)
search_frame.pack(fill="x", padx=10, pady=5)

Label(search_frame, text="Student Name").grid(row=0, column=0)
search_entry = Entry(search_frame)
search_entry.grid(row=0, column=1)

Button(search_frame, text="Search", command=search_student).grid(row=1, column=0, columnspan=2)

# Output
output = Listbox(root, width=90)
output.pack(padx=10, pady=10)

root.mainloop()
