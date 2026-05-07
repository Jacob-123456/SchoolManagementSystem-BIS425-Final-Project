from tkinter import *
from tkinter import ttk
import sys
from mySQL_DB import get_conn

# ---------------- AUTH ----------------
if "verified" not in sys.argv:
    print("Unauthorized access. Please log in through the login screen.")
    sys.exit()

try:
    USER_ID = int(sys.argv[sys.argv.index("verified") + 1])
except (IndexError, ValueError):
    print("No user_id provided.")
    sys.exit()

def get_student():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name FROM students WHERE user_id = %s", (USER_ID,))
        return cursor.fetchone()
    finally:
        conn.close()

student_row = get_student()
if not student_row:
    print("No student account found for this user.")
    sys.exit()

STUDENT_ID, STUDENT_NAME = student_row

# ---------------- DB SETUP ----------------
def setup_db():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        # Add submitted column to assignments if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignment_submissions (
                id INTEGER AUTO_INCREMENT PRIMARY KEY,
                assignment_id INTEGER,
                student_id INTEGER,
                submitted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY(assignment_id) REFERENCES assignments(assignment_id),
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            )
        """)
        conn.commit()
    finally:
        conn.close()

setup_db()

# ---------------- DATA ----------------

def get_my_class():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT classes.class_id, classes.name, subjects.name
            FROM class_students
            JOIN classes ON classes.class_id = class_students.class_id
            JOIN subjects ON subjects.subject_id = classes.subject_id
            WHERE class_students.student_id = %s
            LIMIT 1
        """, (STUDENT_ID,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_assignments(class_id):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                assignments.assignment_id,
                assignments.title,
                assignments.max_score,
                COALESCE(assignment_submissions.submitted, FALSE) AS submitted,
                results.real_score,
                results.letter
            FROM assignments
            LEFT JOIN assignment_submissions 
                ON assignment_submissions.assignment_id = assignments.assignment_id
                AND assignment_submissions.student_id = %s
            LEFT JOIN results
                ON results.assignment_id = assignments.assignment_id
                AND results.student_id = %s
            WHERE assignments.class_id = %s
        """, (STUDENT_ID, STUDENT_ID, class_id))
        return cursor.fetchall()
    finally:
        conn.close()

def get_overall_grade(class_id):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(results.real_score), SUM(results.max_score)
            FROM results
            JOIN assignments ON assignments.assignment_id = results.assignment_id
            WHERE assignments.class_id = %s AND results.student_id = %s
        """, (class_id, STUDENT_ID))
        row = cursor.fetchone()
        if row and row[0] is not None and row[1]:
            total_score, total_max = row
            pct = total_score / total_max * 100
            if pct >= 90: letter = "A"
            elif pct >= 80: letter = "B"
            elif pct >= 70: letter = "C"
            elif pct >= 60: letter = "D"
            else: letter = "F"
            return total_score, total_max, pct, letter
        return None
    finally:
        conn.close()

# ---------------- REFRESH ----------------

def refresh():
    class_row = get_my_class()
    if not class_row:
        class_label.config(text="You are not enrolled in any class.")
        subject_label.config(text="")
        grade_label.config(text="")
        for row in assignment_tree.get_children():
            assignment_tree.delete(row)
        return

    class_id, class_name, subject_name = class_row
    class_label.config(text=f"Class: {class_name}")
    subject_label.config(text=f"Subject: {subject_name}")

    # Assignments
    for row in assignment_tree.get_children():
        assignment_tree.delete(row)

    assignments = get_assignments(class_id)
    for a_id, title, max_score, submitted, real_score, letter in assignments:
        if real_score is not None:
            status = f"Graded ({letter})"
        elif submitted:
            status = "Submitted"
        else:
            status = "Not Submitted"
        score_display = f"{real_score}/{max_score}" if real_score is not None else f"-/{max_score}"
        assignment_tree.insert("", END, values=(a_id, title, score_display, status))

    # Overall grade
    grade = get_overall_grade(class_id)
    if grade:
        total, max_total, pct, letter = grade
        grade_label.config(text=f"Overall Grade: {total}/{max_total}  ({pct:.1f}%)  —  {letter}")
    else:
        grade_label.config(text="Overall Grade: No graded assignments yet.")

def submit_assignment():
    selected = assignment_tree.selection()
    if not selected:
        log("Select an assignment to submit.")
        return

    values = assignment_tree.item(selected[0])["values"]
    assignment_id, title, score, status = values

    if status == "Graded" or "Graded" in str(status):
        log("This assignment has already been graded.")
        return
    if status == "Submitted":
        log("Already submitted.")
        return

    class_row = get_my_class()
    if not class_row:
        log("No class found.")
        return

    conn = get_conn()
    try:
        cursor = conn.cursor()
        # Check if submission row exists
        cursor.execute("""
            SELECT id FROM assignment_submissions
            WHERE assignment_id = %s AND student_id = %s
        """, (assignment_id, STUDENT_ID))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE assignment_submissions SET submitted = TRUE
                WHERE assignment_id = %s AND student_id = %s
            """, (assignment_id, STUDENT_ID))
        else:
            cursor.execute("""
                INSERT INTO assignment_submissions (assignment_id, student_id, submitted)
                VALUES (%s, %s, TRUE)
            """, (assignment_id, STUDENT_ID))
        conn.commit()
        log(f"'{title}' submitted for grading.")
        refresh()
    except Exception as e:
        conn.rollback()
        log(f"Error: {e}")
    finally:
        conn.close()

def log(msg):
    output.config(state=NORMAL)
    output.insert(END, msg + "\n")
    output.see(END)
    output.config(state=DISABLED)

# ---------------- THEME ----------------
BG     = "#1a1a2e"
PANEL  = "#16213e"
ACCENT = "#0f3460"
FG     = "#e0e0e0"
FONT   = ("Segoe UI", 10)

def apply_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="#0d1b2a", foreground=FG,
                    fieldbackground="#0d1b2a", rowheight=24, font=FONT)
    style.configure("Treeview.Heading",
                    background=ACCENT, foreground="white",
                    font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", "#1a5276")])

def make_tree(parent, columns, height=8):
    frame = Frame(parent, bg=PANEL)
    frame.pack(fill=BOTH, expand=True, pady=(4, 0))
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=160)
    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True)
    sb.pack(side=RIGHT, fill=Y)
    return tree

def make_button(parent, text, command, color=None):
    return Button(parent, text=text, command=command,
                  bg=color or ACCENT, fg="white", font=FONT,
                  relief=FLAT, padx=12, pady=5, cursor="hand2",
                  activebackground="#1a5276", activeforeground="white")

def section(parent, title):
    f = Frame(parent, bg=PANEL, padx=12, pady=10)
    f.pack(fill="x", padx=12, pady=(8, 0))
    Label(f, text=title, bg=PANEL, fg="#6fa3d8",
          font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
    Frame(f, bg=ACCENT, height=1).pack(fill="x", pady=(0, 8))
    return f

# ---------------- GUI ----------------

root = Tk()
root.title(f"Student Portal — {STUDENT_NAME}")
root.geometry("800x640")
root.configure(bg=BG)

apply_style()

# Title bar
title_frame = Frame(root, bg=ACCENT, pady=14)
title_frame.pack(fill="x")
Label(title_frame, text="🏫  Student Portal",
      font=("Segoe UI", 14, "bold"), bg=ACCENT, fg="white").pack()
Label(title_frame, text=f"Logged in as {STUDENT_NAME}",
      font=("Segoe UI", 9), bg=ACCENT, fg="#aac4e8").pack()

# Class info
class_info = Frame(root, bg=PANEL, padx=16, pady=12)
class_info.pack(fill="x", padx=12, pady=(10, 0))

class_label = Label(class_info, text="Loading...", bg=PANEL, fg="white",
                    font=("Segoe UI", 12, "bold"))
class_label.pack(anchor="w")

subject_label = Label(class_info, text="", bg=PANEL, fg="#aac4e8", font=FONT)
subject_label.pack(anchor="w")

grade_label = Label(class_info, text="", bg=PANEL, fg="#27ae60",
                    font=("Segoe UI", 11, "bold"))
grade_label.pack(anchor="w", pady=(6, 0))

# Assignments section
sec = section(root, "MY ASSIGNMENTS")
sec.pack_configure(fill="both", expand=True)

assignment_tree = make_tree(sec, ("assignment_id", "title", "score", "status"), height=10)

# Color-code rows by status
def tag_rows():
    assignment_tree.tag_configure("graded", foreground="#27ae60")
    assignment_tree.tag_configure("submitted", foreground="#f39c12")
    assignment_tree.tag_configure("pending", foreground="#e74c3c")

tag_rows()

btn_row = Frame(root, bg=BG, pady=8)
btn_row.pack(fill="x", padx=12)

make_button(btn_row, "📤  Submit for Grading", submit_assignment, color="#0f3460").pack(side=LEFT, padx=(0, 8))
make_button(btn_row, "↻  Refresh", refresh, color="#555").pack(side=LEFT)

# Output log
Frame(root, bg="#333", height=1).pack(fill="x")
output = Text(root, height=3, state=DISABLED, bg="#111",
              fg="#aaa", font=("Consolas", 9), relief=FLAT, padx=10, pady=6)
output.pack(fill="x")

# Startup
refresh()
root.mainloop()