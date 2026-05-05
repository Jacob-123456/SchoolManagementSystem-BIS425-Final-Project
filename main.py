from tkinter import *
from tkinter import ttk
import sqlite3
import subprocess
import sys




# ---------------- REFRESH FUNCTIONS ----------------

def refresh_students():
    for row in student_tree.get_children():
        student_tree.delete(row)
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        student_tree.insert("", END, values=row)
    conn.close()

def refresh_subjects():
    for row in subject_tree.get_children():
        subject_tree.delete(row)
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    for row in cursor.fetchall():
        subject_tree.insert("", END, values=row)
    conn.close()

def refresh_assignments():
    for row in assignment_tree.get_children():
        assignment_tree.delete(row)
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assignments")
    for row in cursor.fetchall():
        assignment_tree.insert("", END, values=row)
    conn.close()

def refresh_results():
    for row in result_tree.get_children():
        result_tree.delete(row)
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results")
    for row in cursor.fetchall():
        result_tree.insert("", END, values=row)
    conn.close()

def refresh_all():
    refresh_students()
    refresh_subjects()
    refresh_assignments()
    refresh_results()

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
    refresh_students()

def add_subject():
    sid = subject_id_entry.get()
    name = subject_name_entry.get()
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO subjects VALUES (?, ?)", (sid, name))
    conn.commit()
    conn.close()
    output.insert(END, "Subject added")
    refresh_subjects()

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
    refresh_assignments()

def add_result():
    student_id = result_student_entry.get()
    assignment_id = result_assignment_entry.get()
    try:
        real_score = float(result_score_entry.get())
        max_score = float(result_score_entry_max.get())
        percentage_score = real_score / max_score * 100
    except:
        output.insert(END, "Invalid score")
        return
    if percentage_score >= 90: letter = "A"
    elif percentage_score >= 80: letter = "B"
    elif percentage_score >= 70: letter = "C"
    elif percentage_score >= 60: letter = "D"
    else: letter = "F"
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO results (student_id, assignment_id, real_score, letter, max_score, percentage_score) VALUES (?, ?, ?, ?, ?, ?)",
                   (student_id, assignment_id, real_score, letter, max_score, percentage_score))
    conn.commit()
    conn.close()
    output.insert(END, "Result added")
    refresh_results()

def search_student():
    name = search_entry.get()
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    query = """
    SELECT students.name, subjects.name, assignments.title, results.percentage_score, results.letter
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

# ---------------- HELPER: make a Treeview ----------------

def make_tree(parent, columns):
    frame = Frame(parent)
    frame.pack(side=LEFT, padx=(20, 0), fill=BOTH, expand=True)

    tree = ttk.Treeview(frame, columns=columns, show="headings", height=3)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    return tree

# ---------------- GUI ----------------


root = Tk()
root.title("School Management System")
root.geometry("900x650")

# --- Student ---
student_frame = LabelFrame(root, text="Student", padx=10, pady=10)
student_frame.pack(fill="x", padx=10, pady=5)

form_s = Frame(student_frame)
form_s.pack(side=LEFT)

Label(form_s, text="Student ID").grid(row=0, column=0)
student_id_entry = Entry(form_s)
student_id_entry.grid(row=0, column=1)

Label(form_s, text="Student Name").grid(row=1, column=0)
student_name_entry = Entry(form_s)
student_name_entry.grid(row=1, column=1)

Button(form_s, text="Add Student", command=add_student).grid(row=2, column=0, columnspan=2)

student_tree = make_tree(student_frame, ("student_id", "name"))

# --- Subject ---
subject_frame = LabelFrame(root, text="Subject", padx=10, pady=10)
subject_frame.pack(fill="x", padx=10, pady=5)

form_sub = Frame(subject_frame)
form_sub.pack(side=LEFT)

Label(form_sub, text="Subject ID").grid(row=0, column=0)
subject_id_entry = Entry(form_sub)
subject_id_entry.grid(row=0, column=1)

Label(form_sub, text="Subject Name").grid(row=1, column=0)
subject_name_entry = Entry(form_sub)
subject_name_entry.grid(row=1, column=1)

Button(form_sub, text="Add Subject", command=add_subject).grid(row=2, column=0, columnspan=2)

subject_tree = make_tree(subject_frame, ("subject_id", "name"))

# --- Assignment ---
assignment_frame = LabelFrame(root, text="Assignment", padx=10, pady=10)
assignment_frame.pack(fill="x", padx=10, pady=5)

form_a = Frame(assignment_frame)
form_a.pack(side=LEFT)

Label(form_a, text="Assignment ID").grid(row=0, column=0)
assignment_id_entry = Entry(form_a)
assignment_id_entry.grid(row=0, column=1)

Label(form_a, text="Subject ID").grid(row=1, column=0)
assignment_subject_entry = Entry(form_a)
assignment_subject_entry.grid(row=1, column=1)

Label(form_a, text="Title").grid(row=2, column=0)
assignment_title_entry = Entry(form_a)
assignment_title_entry.grid(row=2, column=1)

Button(form_a, text="Add Assignment", command=add_assignment).grid(row=3, column=0, columnspan=2)

assignment_tree = make_tree(assignment_frame, ("assignment_id", "subject_id", "title"))

# --- Result ---
result_frame = LabelFrame(root, text="Result", padx=10, pady=10)
result_frame.pack(fill="x", padx=10, pady=5)

form_r = Frame(result_frame)
form_r.pack(side=LEFT)

Label(form_r, text="Student ID").grid(row=0, column=0)
result_student_entry = Entry(form_r)
result_student_entry.grid(row=0, column=1)

Label(form_r, text="Assignment ID").grid(row=1, column=0)
result_assignment_entry = Entry(form_r)
result_assignment_entry.grid(row=1, column=1)

Label(form_r, text="Score").grid(row=2, column=0)
result_score_entry = Entry(form_r)
result_score_entry.grid(row=2, column=1)

Label(form_r, text="Maximum Score").grid(row=3, column=0)
result_score_entry_max = Entry(form_r)
result_score_entry_max.grid(row=3, column=1)

Button(form_r, text="Add Result", command=add_result).grid(row=4, column=0, columnspan=2)

result_tree = make_tree(result_frame, ("id", "student_id", "assignment_id", "real_score", "letter", "max_score", "percentage_score"))

# --- Search ---
search_frame = LabelFrame(root, text="Search", padx=10, pady=10)
search_frame.pack(fill="x", padx=10, pady=5)

Label(search_frame, text="Student Name").grid(row=0, column=0)
search_entry = Entry(search_frame)
search_entry.grid(row=0, column=1)

Button(search_frame, text="Search", command=search_student).grid(row=1, column=0, columnspan=2)

# --- Output ---
output = Listbox(root, width=90)
output.pack(padx=10, pady=10)

# Load existing data on startup
refresh_all()

if "verified" in sys.argv:
    root.mainloop()
else:
    print("Unauthorized access. Please log in through the login screen.")
