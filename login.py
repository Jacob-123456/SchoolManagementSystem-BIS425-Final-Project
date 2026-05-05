from tkinter import *
from tkinter import ttk
import sqlite3
import subprocess
import sys
import importlib.util
import os
import auth

#this checks if you have the bcrypt library, if not it installs it for you. This is used for hashing passwords. 
#It checks if you can do a pip install first, if not it goes through a uv virtual environment which apparantly I have I guess and it makes package installation like 20% harder.
if importlib.util.find_spec("bcrypt") is None:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt"])
    except:
        subprocess.check_call(["uv", "pip", "install", "bcrypt"],
                             env={**os.environ, "VIRTUAL_ENV": ".venv"})

import bcrypt

#this will hash a password
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

#this checks if a password is a bcrypt hash to prevent double hashing.
def is_bcrypt_hash(value: bytes | str) -> bool:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return value.startswith((b"$2a$", b"$2b$", b"$2y$"))

#this will hash all passwords if needed.
def hash_usertable_passwords():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT rowid, password FROM usertable")
    rows = cursor.fetchall()

    for rowid, password in rows:
        if isinstance(password, str):
            raw_password = password.encode("utf-8")
        else:
            raw_password = password

        if is_bcrypt_hash(raw_password):
            continue

        hashed = hash_password(raw_password.decode("utf-8"))
        cursor.execute(
            "UPDATE usertable SET password = ? WHERE rowid = ?",
            (hashed, rowid)
        )

    conn.commit()
    conn.close()

hash_usertable_passwords() #will hash all passwords if needed. Hashed passwords will not be rehashed so the worst this does is use some memory.

#this function does no verification on its own, just opens the main.py file and says the login was verified. Can be changed later if needed for better security.
def open_main():
    subprocess.Popen([sys.executable, "main.py", "verified"])
    root.destroy()  # Close the login window
    subprocess.Popen([sys.executable, "main.py"])
#the actual check of username / password. Will return error if no user found. Will hash the input password and compare to hashed password of the user it's checking.
def login_check():
    username = username_entry.get().strip()
    password = password_entry.get().encode("utf-8")
    account_type = selected_account_type.get()

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, account_type FROM usertable WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result: #checks for valid username
        output.insert(END, "No user found with that username\n")
        return

    stored_username, stored_hash, stored_account_type = result

    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    if bcrypt.checkpw(password, stored_hash) == TRUE: #checks for valid password. password = user input, stored_hash = hash of password from username.
        output.insert(END, f"{account_type} {stored_username} logged in successfully\n")
        if account_type == "Faculty":
            open_main()
    else:
        output.insert(END, "Invalid credentials\n")

def forgot_password():
    output.insert(END, "Password reset functionality is not implemented yet\n")
    #How the hell would I make this work. Most use emails for verification but we don't really do that.

root = Tk()
root.title("Login")
root.geometry("900x650")
    
student_frame = LabelFrame(root, text="Login", padx=10, pady=10)
student_frame.pack(fill="x", padx=10, pady=5)

form_s = Frame(student_frame)
form_s.pack(side=LEFT)

Label(form_s, text="Username").grid(row=0, column=0)
username_entry = Entry(form_s)
username_entry.grid(row=0, column=1)

Label(form_s, text="Password").grid(row=1, column=0)

password_entry = Entry(form_s)
password_entry.grid(row=1, column=1)

selected_account_type = StringVar()
account_type_options = ["Student", "Teacher", "Faculty"]
dropdown = ttk.Combobox(form_s, textvariable=selected_account_type, values=account_type_options, state="readonly")


Label(form_s, text="Account Type").grid(row=2, column=0)
dropdown.grid(row=2, column=1)

login_frame = LabelFrame(root, text="Login", padx=10, pady=10)
login_frame.pack(fill="x", padx=10, pady=5)

Button(login_frame, text="Login", command=login_check).grid(row=3, column=0, columnspan=2)

#adds a line. I thought it would look good but eh. I'm not a fuckass UI designer god bless them they could make this project look so much better.
separator = Frame(root, height=5, bg="grey")
separator.pack(fill="x", padx=10, pady=5)

#debug login frame & button
debug_frame = LabelFrame(root, text="force_login(debug)", padx=10, pady=10)
debug_frame.pack(fill="x", padx=10, pady=5)
Button(debug_frame, text="Login as faculty", command=open_main).grid(row=0, column=0, columnspan=2)

#forgot account frame & button
forgot_account_frame = LabelFrame(root, text="Forgot Account", padx=10, pady=10)
forgot_account_frame.pack(fill="x", padx=10, pady=5)
Button(forgot_account_frame, text="Reset Password", command=forgot_password).grid(row=0, column=0, columnspan=2)

#log output frame
log_label = Label(root, text="Log")

log_label.pack(padx=5, pady=0)

output = Listbox(root, width=50, height=5)
output.pack(padx=5, pady=5)




root.mainloop()
