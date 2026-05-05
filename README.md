# BIS425-Final-Project
For Group 8

Update log:

4/17/26 - Made DB, made student, demerit, parent table. (jacob)

4/29/26 - Additional tables, testing 

5/3/26 - added visible updating table that shows data from db. The treeview function is just a builder function for all 4 tables to be easily made. (jacob)

5/4/26 - Added login file, added auth checker so no one can open and use main.py without logging in from login.py first (jacob)


---------------------------------------------------


**School Management System - Setup Instructions**

1. Make sure you have Python installed and an IDE like VS Code, Jupyter Notebook, or something.
   
3. Install login.py, school.db, main.py, auth.py. **OR download SMS folder.zip and unzip.** It has every file.
   
5. Put the files in a folder together.
   
7. Open the entire folder in the IDE, or make sure each file is in your environment.
   
9. run login file to login (there's a debug force login to main.py).

   
    Placeholder accounts: Username: 1, Pass: 1, account_type: student. User: 2, Pass: 2, account_type: teacher. User: 3, pass: 3, account_type: faculty.
    
11. Run main.py if you want. **There's no verification to check if one is logged in or not, so you can just ignore the login file and run main.py. Fix later**.
    
13. You can use https://sqliteviewer.app/#/school.db/table/results/ to look at the school.db if you do not have SQLite to open .db files.

Running database.py will build a db file that isn't updated like the school.db file is right now. 

Features:
- Add students, subjects, assignments, and results
- Search student results
- Data stored in SQLite database (school.db)

Notes:
- Enter IDs exactly (student_id, subject_id, etc.)
- Run Database.py only if school.db is not included
