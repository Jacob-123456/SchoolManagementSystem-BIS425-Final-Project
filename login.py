from tkinter import *
from tkinter import ttk
import sqlite3
import subprocess
import sys
import importlib.util
import os
import auth

# ── dependency check ──────────────────────────────────────────────────────────
if importlib.util.find_spec("bcrypt") is None:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt"])
    except:
        subprocess.check_call(["uv", "pip", "install", "bcrypt"],
                              env={**os.environ, "VIRTUAL_ENV": ".venv"})

import bcrypt

# ── helpers ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def is_bcrypt_hash(value: bytes | str) -> bool:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return value.startswith((b"$2a$", b"$2b$", b"$2y$"))

def hash_usertable_passwords():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, password FROM usertable")
    for rowid, password in cursor.fetchall():
        raw = password.encode("utf-8") if isinstance(password, str) else password
        if is_bcrypt_hash(raw):
            continue
        cursor.execute("UPDATE usertable SET password = ? WHERE rowid = ?",
                       (hash_password(raw.decode("utf-8")), rowid))
    conn.commit()
    conn.close()

def hash_usertable_security_questions():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, security_question_answer FROM usertable")
    for rowid, answer in cursor.fetchall():
        raw = answer.encode("utf-8") if isinstance(answer, str) else answer
        if is_bcrypt_hash(raw):
            continue
        cursor.execute("UPDATE usertable SET security_question_answer = ? WHERE rowid = ?",
                       (hash_password(raw.decode("utf-8")), rowid))
    conn.commit()
    conn.close()

hash_usertable_passwords()
hash_usertable_security_questions()

# ── launchers ─────────────────────────────────────────────────────────────────
def open_teacher(user_id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, os.path.join(base_dir, "teacher.py"), "verified", str(user_id)])
    root.destroy()

def open_main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, os.path.join(base_dir, "main.py"), "verified"])
    root.destroy()

# ── login logic ───────────────────────────────────────────────────────────────
def login_check():
    username = username_entry.get().strip()
    password = password_entry.get().encode("utf-8")
    account_type = selected_account_type.get()

    if not username or not password or not account_type:
        log("Please fill in all fields.")
        return

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, password, account_type FROM usertable WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        log("No user found with that username.")
        return

    user_id, stored_username, stored_hash, stored_account_type = result

    if account_type != stored_account_type:
        log(f"This account is not registered as '{account_type}'.")
        return

    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    if bcrypt.checkpw(password, stored_hash):
        log(f"Logged in as {stored_username} ({stored_account_type})")
        if account_type == "Faculty":
            open_main()
        elif account_type == "Teacher":
            open_teacher(user_id)
    else:
        log("Incorrect password.")

def log(msg):
    output.config(state=NORMAL)
    output.insert(END, msg + "\n")
    output.see(END)
    output.config(state=DISABLED)

# ── forgot password ───────────────────────────────────────────────────────────
def forgot_password_1():
    global forgot_window, password_output
    global forgot_password1_username_input, username_entry_forgot, forgot_password_button_1

    forgot_window = Toplevel(root)
    forgot_window.title("Reset Password")
    forgot_window.geometry("420x320")
    forgot_window.resizable(False, False)
    forgot_window.configure(bg=BG)

    Label(forgot_window, text="Reset Password", font=("Segoe UI", 13, "bold"),
          bg=BG, fg=FG).pack(pady=(18, 8))

    form = Frame(forgot_window, bg=BG)
    form.pack(padx=30, fill="x")

    forgot_password1_username_input = Label(form, text="Username", bg=BG, fg=FG, font=FONT)
    forgot_password1_username_input.grid(row=0, column=0, sticky="w", pady=4)
    username_entry_forgot = Entry(form, width=28, font=FONT)
    username_entry_forgot.grid(row=0, column=1, pady=4, padx=(8, 0))

    forgot_password_button_1 = Button(forgot_window, text="Next →", command=forgot_password_2,
                                      bg=ACCENT, fg="white", font=FONT, relief=FLAT,
                                      padx=16, pady=6, cursor="hand2")
    forgot_password_button_1.pack(pady=12)

    Frame(forgot_window, bg="#444", height=1).pack(fill="x", padx=20)

    password_output = Text(forgot_window, height=5, state=DISABLED, bg="#1e1e1e",
                           fg="#aaa", font=("Consolas", 9), relief=FLAT, padx=8, pady=4)
    password_output.pack(fill="x", padx=20, pady=10)


def forgot_password_2():
    global username_entry_forgot_data
    username_entry_forgot_data = username_entry_forgot.get().strip()

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM usertable WHERE username=?", (username_entry_forgot_data,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        forgot_window.destroy()
        forgot_password_1()
        forgot_log("No user found with that username.")
        return

    forgot_password1_username_input.destroy()
    username_entry_forgot.destroy()
    forgot_password_button_1.destroy()

    form2 = Frame(forgot_window, bg=BG)
    form2.pack(padx=30, fill="x")

    lbl = Label(form2, text="First pet's name?", bg=BG, fg=FG, font=FONT)
    lbl.grid(row=0, column=0, sticky="w", pady=4)
    sec_entry = Entry(form2, width=28, font=FONT)
    sec_entry.grid(row=0, column=1, pady=4, padx=(8, 0))

    btn_frame = Frame(forgot_window, bg=BG)
    btn_frame.pack(pady=8)

    def submit():
        global security_question_entry_global
        security_question_entry_global = sec_entry.get().strip()
        lbl.destroy()
        sec_entry.destroy()
        btn_frame.destroy()
        forgot_password_3()

    Button(btn_frame, text="Next →", command=submit,
           bg=ACCENT, fg="white", font=FONT, relief=FLAT, padx=16, pady=6, cursor="hand2").pack(side=LEFT, padx=5)
    Button(btn_frame, text="← Back", command=lambda: [forgot_window.destroy(), forgot_password_1()],
           bg="#555", fg="white", font=FONT, relief=FLAT, padx=16, pady=6, cursor="hand2").pack(side=LEFT, padx=5)


def forgot_password_3():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT security_question_answer FROM usertable WHERE username=?", (username_entry_forgot_data,))
    result = cursor.fetchone()
    conn.close()

    if bcrypt.checkpw(security_question_entry_global.encode("utf-8"), result[0]):
        forgot_log("Security question correct. Enter your new password.")

        form3 = Frame(forgot_window, bg=BG)
        form3.pack(padx=30, fill="x")

        Label(form3, text="New Password", bg=BG, fg=FG, font=FONT).grid(row=0, column=0, sticky="w", pady=4)
        global new_password_entry
        new_password_entry = Entry(form3, width=28, font=FONT, show="*")
        new_password_entry.grid(row=0, column=1, pady=4, padx=(8, 0))

        btn_frame = Frame(forgot_window, bg=BG)
        btn_frame.pack(pady=8)

        Button(btn_frame, text="Reset Password", command=reset_password,
               bg="#27ae60", fg="white", font=FONT, relief=FLAT, padx=16, pady=6, cursor="hand2").pack(side=LEFT, padx=5)
        Button(btn_frame, text="← Back", command=lambda: [forgot_window.destroy(), forgot_password_1()],
               bg="#555", fg="white", font=FONT, relief=FLAT, padx=16, pady=6, cursor="hand2").pack(side=LEFT, padx=5)
    else:
        forgot_log("Incorrect answer. Try again.")
        forgot_password_2()

def forgot_log(msg):
    password_output.config(state=NORMAL)
    password_output.insert(END, msg + "\n")
    password_output.see(END)
    password_output.config(state=DISABLED)

def reset_password():
    new_password = new_password_entry.get().strip()
    if not new_password:
        forgot_log("Password cannot be empty.")
        return
    hashed = hash_password(new_password)
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE usertable SET password=? WHERE username=?", (hashed, username_entry_forgot_data))
    conn.commit()
    conn.close()
    forgot_log("Password reset successfully. You may close this window.")

# ── theme ─────────────────────────────────────────────────────────────────────
BG     = "#1a1a2e"
PANEL  = "#16213e"
ACCENT = "#0f3460"
FG     = "#e0e0e0"
FONT   = ("Segoe UI", 10)

# ── root window ───────────────────────────────────────────────────────────────
root = Tk()
root.title("School Management System — Login")
root.geometry("420x520")
root.resizable(False, False)
root.configure(bg=BG)

# ── title ─────────────────────────────────────────────────────────────────────
title_frame = Frame(root, bg=ACCENT, pady=18)
title_frame.pack(fill="x")
Label(title_frame, text="🏫  School Management System",
      font=("Segoe UI", 14, "bold"), bg=ACCENT, fg="white").pack()
Label(title_frame, text="Sign in Page",
      font=("Segoe UI", 9), bg=ACCENT, fg="#aac4e8").pack()

# ── login card ────────────────────────────────────────────────────────────────
card = Frame(root, bg=PANEL, padx=30, pady=24)
card.pack(padx=30, pady=24, fill="x")

def field(parent, label, row, hide=False):
    Label(parent, text=label, bg=PANEL, fg=FG, font=FONT, anchor="w").grid(
        row=row, column=0, sticky="w", pady=(8, 2), columnspan=2)
    e = Entry(parent, font=FONT, width=30, show="*" if hide else "", bg="#0d1b2a",
              fg="white", insertbackground="white", relief=FLAT, bd=6)
    e.grid(row=row+1, column=0, columnspan=2, sticky="ew", ipady=4)
    return e

card.columnconfigure(0, weight=1)

Label(card, text="Username", bg=PANEL, fg=FG, font=FONT, anchor="w").grid(
    row=0, column=0, sticky="w", pady=(0, 2), columnspan=2)
username_entry = Entry(card, font=FONT, width=30, bg="#0d1b2a", fg="white",
                       insertbackground="white", relief=FLAT, bd=6)
username_entry.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=4)

Label(card, text="Password", bg=PANEL, fg=FG, font=FONT, anchor="w").grid(
    row=2, column=0, sticky="w", pady=(10, 2), columnspan=2)
password_entry = Entry(card, font=FONT, width=30, show="*", bg="#0d1b2a", fg="white",
                       insertbackground="white", relief=FLAT, bd=6)
password_entry.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=4)

Label(card, text="Account Type", bg=PANEL, fg=FG, font=FONT, anchor="w").grid(
    row=4, column=0, sticky="w", pady=(10, 2), columnspan=2)
selected_account_type = StringVar()
dropdown = ttk.Combobox(card, textvariable=selected_account_type,
                        values=["Student", "Teacher", "Faculty"],
                        state="readonly", font=FONT, width=28)
dropdown.grid(row=5, column=0, columnspan=2, sticky="ew")

Button(card, text="Login", command=login_check,
       bg=ACCENT, fg="white", font=("Segoe UI", 11, "bold"),
       relief=FLAT, pady=8, cursor="hand2", activebackground="#1a5276",
       activeforeground="white").grid(row=6, column=0, columnspan=2, sticky="ew", pady=(18, 0))

# ── secondary actions ─────────────────────────────────────────────────────────
actions = Frame(root, bg=BG)
actions.pack(fill="x", padx=30)

Button(actions, text="Forgot Password?", command=forgot_password_1,
       bg=BG, fg="#6fa3d8", font=("Segoe UI", 9), relief=FLAT,
       cursor="hand2", activebackground=BG, activeforeground="white").pack(side=LEFT)

Button(actions, text="Debug: Login as Faculty", command=open_main,
       bg=BG, fg="#666", font=("Segoe UI", 9), relief=FLAT,
       cursor="hand2", activebackground=BG, activeforeground="white").pack(side=RIGHT)

# ── log output ────────────────────────────────────────────────────────────────
Frame(root, bg="#333", height=1).pack(fill="x", padx=20, pady=(16, 0))

output = Text(root, height=5, state=DISABLED, bg="#111",
              fg="#aaa", font=("Consolas", 9), relief=FLAT, padx=10, pady=6)
output.pack(fill="x", padx=20, pady=8)

root.mainloop()
