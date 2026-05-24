# BIS425-Final-Project - Group 8



---------------------------------------------------


**School Management System - Setup Instructions**

1. Make sure you have Python installed and an IDE like VS Code, Jupyter Notebook, or something.
   
3. It's recommended to just install SMS folder.zip and unzip it.
   
5. Put the files in a folder together.

6. Open MySQL, log in to localhost, import the SQL script, and run it.
   
7. Open the entire folder in the IDE, or make sure each file is in your environment.
   
8. Run the login file FIRST so you can log in. There's a debug login for faculty to create accounts if you wish.


Features:
- Add students, subjects, assignments, and results
- Search student results

Notes:
- Enter IDs exactly (student_id, subject_id, etc.)


Update log:

4/17/26 - Made DB, made student, demerit, parent table. (jacob)

4/29/26 - Additional tables, testing (chris)

5/3/26 - added visible updating table that shows data from db. The treeview function is just a builder function for all 4 tables to be easily made. (jacob)

5/4/26 - Added login file, added auth checker so no one can open and use main.py without logging in from login.py first (jacob)

5/5/26 - added password resetting w/ security question check to reset password. (jacob)

5/6/26 - added tabs in main.py and account creation (jacob).

5/7/26 - added teacher.py, UI redesigned in login.py. Database now hosted on mysql not sqlite, added student.py, removed main.py unneeded functions. (jacob).

5/8/26 - final bug fixes.

