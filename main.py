from tkinter import *
from tkinter import ttk
import sys
from mySQL_DB import get_conn


# ---------------- REFRESH FUNCTIONS ----------------

def refresh_students():
    for row in student_tree.get_children():
        student_tree.delete(row)
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        for row in cursor.fetchall():
            student_tree.insert("", END, values=row)
    finally:
        conn.close()

def refresh_subjects():
    for row in subject_tree.get_children():
        subject_tree.delete(row)
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects")
        for row in cursor.fetchall():
            subject_tree.insert("", END, values=row)
    finally:
        conn.close()

def refresh_assignments():
    for row in assignment_tree.get_children():
        assignment_tree.delete(row)
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assignments")
        for row in cursor.fetchall():
            assignment_tree.insert("", END, values=row)
    finally:
        conn.close()

def refresh_results():
    for row in result_tree.get_children():
        result_tree.delete(row)
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM results")
        for row in cursor.fetchall():
            result_tree.insert("", END, values=row)
    finally:
        conn.close()

def refresh_all():
    refresh_students()
    refresh_subjects()
    refresh_assignments()
    refresh_results()


# ---------------- FUNCTIONS ----------------


def add_subject():
    sid = subject_id_entry.get()
    name = subject_name_entry.get()
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (subject_id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name)", (sid, name))
        conn.commit()
        output.insert(END, "Subject added")
        refresh_subjects()
    except Exception as e:
        conn.rollback()
        output.insert(END, f"Error: {e}")
    finally:
        conn.close()


def search_student():
    name = search_entry.get()
    conn = get_conn()
    try:
        cursor = conn.cursor()
        query = """
        SELECT students.name, subjects.name, assignments.title, results.percentage_score, results.letter
        FROM students
        JOIN results ON students.student_id = results.student_id
        JOIN assignments ON assignments.assignment_id = results.assignment_id
        JOIN subjects ON subjects.subject_id = assignments.class_id
        WHERE students.name LIKE %s
        """
        cursor.execute(query, ('%' + name + '%',))
        rows = cursor.fetchall()
        output.delete(0, END)
        if rows:
            for row in rows:
                output.insert(END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]:.1f}% ({row[4]})")
        else:
            output.insert(END, "No results found")
    except Exception as e:
        output.insert(END, f"Error: {e}")
    finally:
        conn.close()

def create_account():
    username = username_entry.get()
    password = password_entry.get()
    account_type = selected_account_type.get()
    security_answer = security_question_entry.get()
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()

    if not username or not password or not account_type or not security_answer:
        output2.insert(END, "All fields are required\n")
        return

    if not first_name or not last_name:
        output2.insert(END, "First and last name required\n")
        return

    conn = get_conn()
    try:
        cursor = conn.cursor()

        # Check if username exists
        cursor.execute("SELECT * FROM usertable WHERE username = %s", (username,))
        if cursor.fetchone():
            output2.insert(END, "Username already exists\n")
            return

        # Insert into usertable
        cursor.execute("""
            INSERT INTO usertable (username, password, account_type, security_question_answer)
            VALUES (%s, %s, %s, %s)
        """, (username, password, account_type, security_answer))

        user_id = cursor.lastrowid

        # Insert into category table
        if account_type == "Student":
            cursor.execute(
                "INSERT INTO students (name, user_id) VALUES (%s, %s)",
                (first_name + " " + last_name, user_id)
            )
        elif account_type == "Teacher":
            cursor.execute(
                "INSERT INTO teachers (name, user_id) VALUES (%s, %s)",
                (first_name + " " + last_name, user_id)
            )
        elif account_type == "Faculty":
            cursor.execute(
                "INSERT INTO faculty (name, user_id) VALUES (%s, %s)",
                (first_name + " " + last_name, user_id)
            )

        conn.commit()
        output2.insert(END, "Account created successfully\n")
        refresh_all()

    except Exception as e:
        conn.rollback()
        output2.insert(END, f"Error: {e}\n")
    finally:
        conn.close()


# ---------------- HELPER ----------------

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

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab1 = Frame(notebook)
notebook.add(tab1, text="Dashboard")
notebook.bind("<<NotebookTabChanged>>", lambda e: refresh_all())

tab2 = Frame(notebook)
notebook.add(tab2, text="Create & Manage Accounts")

# --- Student ---
student_frame = LabelFrame(tab1, text="Student", padx=10, pady=10)
student_frame.pack(fill="x", padx=10, pady=5)

form_s = Frame(student_frame)
form_s.pack(side=LEFT)


student_tree = make_tree(student_frame, ("student_id", "name", "user_id"))

# --- Subject ---
subject_frame = LabelFrame(tab1, text="Subject", padx=10, pady=10)
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
assignment_frame = LabelFrame(tab1, text="Assignment", padx=10, pady=10)
assignment_frame.pack(fill="x", padx=10, pady=5)

form_a = Frame(assignment_frame)
form_a.pack(side=LEFT)


assignment_tree = make_tree(assignment_frame, ("assignment_id", "subject_id", "title","max_score"))

# --- Result ---
result_frame = LabelFrame(tab1, text="Result", padx=10, pady=10)
result_frame.pack(fill="x", padx=10, pady=5)

form_r = Frame(result_frame)
form_r.pack(side=LEFT)


result_tree = make_tree(result_frame, ("id", "student_id", "assignment_id", "real_score", "letter", "max_score", "percentage_score"))

# --- Search ---
search_frame = LabelFrame(tab1, text="Search", padx=10, pady=10)
search_frame.pack(fill="x", padx=10, pady=5)

Label(search_frame, text="Student Name").grid(row=0, column=0)
search_entry = Entry(search_frame)
search_entry.grid(row=0, column=1)

Button(search_frame, text="Search", command=search_student).grid(row=1, column=0, columnspan=2)

# --- Output ---
output = Listbox(tab1, width=90)
output.pack(padx=10, pady=10)

# ---------------- TAB 2 ----------------

create_account_frame = LabelFrame(tab2, text="Create Account", padx=10, pady=10)
create_account_frame.grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky="ew")

Label(create_account_frame, text="First name").grid(row=0, column=1)
first_name_entry = Entry(create_account_frame)
first_name_entry.grid(row=0, column=2)

Label(create_account_frame, text="Last name").grid(row=1, column=1)
last_name_entry = Entry(create_account_frame)
last_name_entry.grid(row=1, column=2)

Label(create_account_frame, text="Username").grid(row=0, column=3)
username_entry = Entry(create_account_frame)
username_entry.grid(row=0, column=4)

Label(create_account_frame, text="Password").grid(row=1, column=3)
password_entry = Entry(create_account_frame, show="*")
password_entry.grid(row=1, column=4)

selected_account_type = StringVar()
Label(create_account_frame, text="Account Type").grid(row=2, column=3)
account_type_options = ["Student", "Teacher", "Faculty"]
account_type_create_account = ttk.Combobox(create_account_frame, textvariable=selected_account_type, values=account_type_options, state="readonly")
account_type_create_account.grid(row=2, column=4)

Label(create_account_frame, text="What is the user's first pet's name?").grid(row=3, column=3)
security_question_entry = Entry(create_account_frame)
security_question_entry.grid(row=3, column=4)

Button(create_account_frame, text="Create Account", command=create_account).grid(row=4, column=0, columnspan=1)

output2 = Listbox(tab2, width=50, height=10)
output2.grid(row=5, column=0, padx=10, pady=10)

# ---------------- STARTUP ----------------

refresh_all()

if "verified" in sys.argv:
    root.mainloop()
else:
    print("Unauthorized access. Please log in through the login screen.")
