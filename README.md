# BIS425-Final-Project
For Group 8

Update log:

4/17/26 - Made DB, made student, demerit, parent table.

4/29/26 - Additional tables, testing 

5/3/26 - added visible updating table that shows data from db. The treeview function is just a builder function for all 4 tables to be easily made.

School Management System - Setup Instructions

1. Make sure Python is installed

2. Open Command Prompt in the folder

3. Run the application:
   python main.py

4. If database is missing, run:
   python Database.py

5. You can use https://sqliteviewer.app/#/school.db/table/results/ to look at the school.db if you do not have sqllite to open .db files. You shouldn't need to since the tables all connect to school.db on the gui.

Features:
- Add students, subjects, assignments, and results
- Search student results
- Data stored in SQLite database (school.db)

Notes:
- Enter IDs exactly (student_id, subject_id, etc.)
- Run Database.py only if school.db is not included
