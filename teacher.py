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

def get_teacher_id():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_id, name FROM teachers WHERE user_id = %s", (USER_ID,))
        return cursor.fetchone()
    finally:
        conn.close()

teacher_row = get_teacher_id()
if not teacher_row:
    print("No teacher account found for this user.")
    sys.exit()

TEACHER_ID, TEACHER_NAME = teacher_row


# ---------------- REFRESH ----------------

def get_my_classes():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT classes.class_id, classes.name, subjects.name
            FROM classes
            JOIN subjects ON subjects.subject_id = classes.subject_id
            WHERE classes.teacher_id = %s
        """, (TEACHER_ID,))
        return cursor.fetchall()
    finally:
        conn.close()

def refresh_class_dropdown():
    classes = get_my_classes()
    class_map.clear()
    labels = []
    for class_id, class_name, subject_name in classes:
        label = f"{class_name} ({subject_name})"
        labels.append(label)
        class_map[label] = class_id
    class_dropdown["values"] = labels
    grade_class_dropdown["values"] = labels
    enroll_class_dropdown["values"] = labels
    if labels:
        class_var.set(labels[0])
        grade_class_var.set(labels[0])
        enroll_class_var.set(labels[0])

def refresh_my_classes_tree():
    for row in my_classes_tree.get_children():
        my_classes_tree.delete(row)
    for class_id, class_name, subject_name in get_my_classes():
        conn = get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM class_students WHERE class_id = %s", (class_id,))
            count = cursor.fetchone()[0]
        finally:
            conn.close()
        my_classes_tree.insert("", END, values=(class_id, class_name, subject_name, count))

def refresh_assignments_tree():
    for row in assignment_tree.get_children():
        assignment_tree.delete(row)
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT assignments.assignment_id, classes.name, assignments.title, assignments.max_score
            FROM assignments
            JOIN classes ON classes.class_id = assignments.class_id
            WHERE classes.teacher_id = %s
        """, (TEACHER_ID,))
        for row in cursor.fetchall():
            assignment_tree.insert("", END, values=row)
    finally:
        conn.close()

def refresh_ungraded():
    for row in ungraded_tree.get_children():
        ungraded_tree.delete(row)
    label = grade_class_var.get()
    if not label or label not in class_map:
        return
    class_id = class_map[label]
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT students.student_id, students.name, assignments.assignment_id, assignments.title, assignments.max_score
            FROM class_students
            JOIN students ON students.student_id = class_students.student_id
            JOIN assignments ON assignments.class_id = %s
            JOIN assignment_submissions 
                ON assignment_submissions.assignment_id = assignments.assignment_id
                AND assignment_submissions.student_id = students.student_id
                AND assignment_submissions.submitted = TRUE
            WHERE class_students.class_id = %s
            AND NOT EXISTS (
                SELECT 1 FROM results
                WHERE results.student_id = students.student_id
                AND results.assignment_id = assignments.assignment_id
    )
""", (class_id, class_id))
        for row in cursor.fetchall():
            ungraded_tree.insert("", END, values=row)
    finally:
        conn.close()

def refresh_graded():
    for row in graded_tree.get_children():
        graded_tree.delete(row)
    label = grade_class_var.get()
    if not label or label not in class_map:
        return
    class_id = class_map[label]
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT students.name, assignments.title, results.real_score, results.max_score, results.percentage_score, results.letter
            FROM results
            JOIN students ON students.student_id = results.student_id
            JOIN assignments ON assignments.assignment_id = results.assignment_id
            WHERE assignments.class_id = %s
        """, (class_id,))
        for row in cursor.fetchall():
            graded_tree.insert("", END, values=row)
    finally:
        conn.close()

def refresh_enroll_students():
    for row in enroll_student_tree.get_children():
        enroll_student_tree.delete(row)
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name FROM students")
        for row in cursor.fetchall():
            enroll_student_tree.insert("", END, values=row)
    finally:
        conn.close()

def refresh_all():
    refresh_my_classes_tree()
    refresh_assignments_tree()
    refresh_class_dropdown()
    refresh_ungraded()
    refresh_graded()
    refresh_enroll_students()

def refresh_subject_dropdown():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT subject_id, name FROM subjects")
        rows = cursor.fetchall()
        subject_map.clear()
        labels = []
        for sid, name in rows:
            label = f"{name} ({sid})"
            labels.append(label)
            subject_map[label] = sid
        subject_dropdown["values"] = labels
        if labels:
            subject_var.set(labels[0])
    finally:
        conn.close()

# ---------------- ACTIONS ----------------

def create_class():
    name = class_name_entry.get().strip()
    subject_label = subject_var.get()
    if not name or subject_label not in subject_map:
        log("Fill in all class fields.")
        return
    subject_id = subject_map[subject_label]
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO classes (name, teacher_id, subject_id) VALUES (%s, %s, %s)",
            (name, TEACHER_ID, subject_id)
        )
        conn.commit()
        log(f"Class '{name}' created.")
        refresh_all()
        refresh_subject_dropdown()
    except Exception as e:
        conn.rollback()
        log(f"Error: {e}")
    finally:
        conn.close()

def enroll_student():
    label = enroll_class_var.get()
    selected = enroll_student_tree.selection()
    if not label or label not in class_map:
        log("Select a class.")
        return
    if not selected:
        log("Select a student to enroll.")
        return
    class_id = class_map[label]
    student_id = enroll_student_tree.item(selected[0])["values"][0]
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM class_students WHERE class_id = %s AND student_id = %s",
            (class_id, student_id)
        )
        if cursor.fetchone():
            log("Student already enrolled in this class.")
            return
        cursor.execute(
            "INSERT INTO class_students (class_id, student_id) VALUES (%s, %s)",
            (class_id, student_id)
        )
        conn.commit()
        log("Student enrolled successfully.")
        refresh_my_classes_tree()
    except Exception as e:
        conn.rollback()
        log(f"Error: {e}")
    finally:
        conn.close()

def create_assignment():
    label = class_var.get()
    title = assignment_title_entry.get().strip()
    try:
        max_score = float(assignment_max_entry.get())
    except ValueError:
        log("Max score must be a number.")
        return
    if not label or label not in class_map or not title:
        log("Fill in all assignment fields.")
        return
    class_id = class_map[label]
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO assignments (class_id, title, max_score) VALUES (%s, %s, %s)",
            (class_id, title, max_score)
        )
        conn.commit()
        log(f"Assignment '{title}' created.")
        refresh_assignments_tree()
        refresh_ungraded()
    except Exception as e:
        conn.rollback()
        log(f"Error: {e}")
    finally:
        conn.close()

def grade_selected():
    selected = ungraded_tree.selection()
    if not selected:
        log("Select a row to grade.")
        return

    try:
        score = float(grade_score_entry.get())
    except ValueError:
        log("Enter a valid score.")
        return

    values = ungraded_tree.item(selected[0])["values"]
    student_id, student_name, assignment_id, title, max_score = values
    max_score = float(max_score)

    conn = get_conn()
    cursor = conn.cursor()

    # ---------------- VALIDATION ----------------
    cursor.execute("""
        SELECT 1
        FROM assignment_submissions
        WHERE student_id = %s
        AND assignment_id = %s
        AND submitted = TRUE
    """, (student_id, assignment_id))

    if not cursor.fetchone():
        log("Cannot grade: student has not submitted this assignment.")
        conn.close()
        return

    # ---------------- GRADE ----------------
    percentage = score / max_score * 100

    if percentage >= 90: letter = "A"
    elif percentage >= 80: letter = "B"
    elif percentage >= 70: letter = "C"
    elif percentage >= 60: letter = "D"
    else: letter = "F"

    try:
        cursor.execute("""
            INSERT INTO results (student_id, assignment_id, real_score, letter, max_score, percentage_score)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, assignment_id, score, letter, max_score, percentage))

        conn.commit()

        log(f"Graded {student_name}: {score}/{max_score} ({letter})")

        grade_score_entry.delete(0, END)
        refresh_ungraded()
        refresh_graded()

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

def apply_treeview_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="#0d1b2a",
                    foreground=FG,
                    fieldbackground="#0d1b2a",
                    rowheight=24,
                    font=FONT)
    style.configure("Treeview.Heading",
                    background=ACCENT,
                    foreground="white",
                    font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", "#1a5276")])
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL, foreground=FG,
                    font=("Segoe UI", 10), padding=[14, 1])
    style.map("TNotebook.Tab", background=[("selected", ACCENT)],
              foreground=[("selected", "white")])
    style.configure("TCombobox", fieldbackground="#0d1b2a", background=ACCENT,
                    foreground="white", selectbackground=ACCENT)

def make_tree(parent, columns, height=5):
    frame = Frame(parent, bg=PANEL)
    frame.pack(fill=BOTH, expand=True, pady=(4, 0))
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=130)
    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True)
    sb.pack(side=RIGHT, fill=Y)
    return tree

def make_entry(parent, width=20):
    return Entry(parent, font=FONT, width=width, bg="#0d1b2a",
                 fg="white", insertbackground="white", relief=FLAT, bd=6)

def make_button(parent, text, command, color=None):
    return Button(parent, text=text, command=command,
                  bg=color or ACCENT, fg="white", font=FONT,
                  relief=FLAT, padx=12, pady=5, cursor="hand2",
                  activebackground="#1a5276", activeforeground="white")

def make_combo(parent, var, width=28):
    return ttk.Combobox(parent, textvariable=var, state="readonly",
                        font=FONT, width=width)

def section(parent, title):
    f = Frame(parent, bg=PANEL, padx=12, pady=10)
    f.pack(fill="x", padx=12, pady=(8, 0))
    Label(f, text=title, bg=PANEL, fg="#6fa3d8",
          font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
    Frame(f, bg=ACCENT, height=1).pack(fill="x", pady=(0, 8))
    return f

def lbl(parent, text):
    return Label(parent, text=text, bg=PANEL, fg=FG, font=FONT)

# ---------------- ROOT ----------------

root = Tk()
root.title(f"Teacher Portal — {TEACHER_NAME}")
root.geometry("1050x720")
root.configure(bg=BG)

apply_treeview_style()

# Title bar
title_frame = Frame(root, bg=ACCENT, pady=14)
title_frame.pack(fill="x")

Label(title_frame, text=f"Logged in as {TEACHER_NAME}",
      font=("Segoe UI", 9), bg=ACCENT, fg="#aac4e8").pack()

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)
notebook.bind("<<NotebookTabChanged>>", lambda e: refresh_all())

tab_classes = Frame(notebook, bg=BG)
notebook.add(tab_classes, text="  My Classes  ")

tab_assignments = Frame(notebook, bg=BG)
notebook.add(tab_assignments, text="  Assignments  ")

tab_grade = Frame(notebook, bg=BG)
notebook.add(tab_grade, text="  Grade  ")

# ── TAB 1: My Classes ──────────────────────────────────────────────────────

sec1 = section(tab_classes, "CREATE CLASS")
row1 = Frame(sec1, bg=PANEL)
row1.pack(fill="x")

lbl(row1, "Class Name").grid(row=0, column=0, sticky="w", padx=(0, 6))
class_name_entry = make_entry(row1, width=18)
class_name_entry.grid(row=0, column=1, padx=(0, 16))

subject_map = {}
subject_var = StringVar()
lbl(row1, "Subject").grid(row=0, column=2, sticky="w", padx=(0, 6))
subject_dropdown = make_combo(row1, subject_var, width=22)
subject_dropdown.grid(row=0, column=3, padx=(0, 16))

make_button(row1, "＋ Create Class", create_class).grid(row=0, column=4)

sec2 = section(tab_classes, "MY CLASSES")
my_classes_tree = make_tree(sec2, ("class_id", "name", "subject", "students"), height=5)

sec3 = section(tab_classes, "ENROLL STUDENT")
enroll_row = Frame(sec3, bg=PANEL)
enroll_row.pack(fill="x", pady=(0, 8))

enroll_class_var = StringVar()
lbl(enroll_row, "Class").pack(side=LEFT, padx=(0, 6))
enroll_class_dropdown = make_combo(enroll_row, enroll_class_var, width=28)
enroll_class_dropdown.pack(side=LEFT, padx=(0, 12))
make_button(enroll_row, "Enroll Selected ↓", enroll_student).pack(side=LEFT)

enroll_student_tree = make_tree(sec3, ("student_id", "name"), height=4)

# ── TAB 2: Assignments ─────────────────────────────────────────────────────

sec4 = section(tab_assignments, "CREATE ASSIGNMENT")
row4 = Frame(sec4, bg=PANEL)
row4.pack(fill="x")

class_map = {}
class_var = StringVar()
lbl(row4, "Class").grid(row=0, column=0, sticky="w", padx=(0, 6))
class_dropdown = make_combo(row4, class_var, width=22)
class_dropdown.grid(row=0, column=1, padx=(0, 16))

lbl(row4, "Title").grid(row=0, column=2, sticky="w", padx=(0, 6))
assignment_title_entry = make_entry(row4, width=22)
assignment_title_entry.grid(row=0, column=3, padx=(0, 16))

lbl(row4, "Max Score").grid(row=0, column=4, sticky="w", padx=(0, 6))
assignment_max_entry = make_entry(row4, width=8)
assignment_max_entry.grid(row=0, column=5, padx=(0, 16))

make_button(row4, "＋ Create Assignment", create_assignment).grid(row=0, column=6)

sec5 = section(tab_assignments, "ALL MY ASSIGNMENTS")
assignment_tree = make_tree(sec5, ("assignment_id", "class", "title", "max_score"), height=10)

# ── TAB 3: Grade ───────────────────────────────────────────────────────────

sec6 = section(tab_grade, "SELECT CLASS")
grade_top = Frame(sec6, bg=PANEL)
grade_top.pack(fill="x")

grade_class_var = StringVar()
lbl(grade_top, "Class").pack(side=LEFT, padx=(0, 6))
grade_class_dropdown = make_combo(grade_top, grade_class_var, width=30)
grade_class_dropdown.pack(side=LEFT, padx=(0, 12))
grade_class_var.trace("w", lambda *a: (refresh_ungraded(), refresh_graded()))
make_button(grade_top, "↻ Refresh", lambda: (refresh_ungraded(), refresh_graded())).pack(side=LEFT)

sec7 = section(tab_grade, "UNGRADED — select a row, enter score, then submit")
ungraded_tree = make_tree(sec7, ("student_id", "student_name", "assignment_id", "title", "max_score"), height=5)

grade_input = Frame(sec7, bg=PANEL, pady=8)
grade_input.pack(fill="x")
lbl(grade_input, "Score").pack(side=LEFT, padx=(0, 6))
grade_score_entry = make_entry(grade_input, width=8)
grade_score_entry.pack(side=LEFT, padx=(0, 10))
make_button(grade_input, "✔ Submit Grade", grade_selected, color="#27ae60").pack(side=LEFT)

sec8 = section(tab_grade, "GRADED")
graded_tree = make_tree(sec8, ("student", "assignment", "score", "max", "percent", "letter"), height=5)

# ── Output log ─────────────────────────────────────────────────────────────
Frame(root, bg="#333", height=1).pack(fill="x")
output = Text(root, height=3, state=DISABLED, bg="#111",
              fg="#aaa", font=("Consolas", 9), relief=FLAT, padx=10, pady=6)
output.pack(fill="x")

# ── Startup ────────────────────────────────────────────────────────────────
refresh_subject_dropdown()
refresh_all()

root.mainloop()