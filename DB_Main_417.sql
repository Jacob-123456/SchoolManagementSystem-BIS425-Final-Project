CREATE DATABASE IF NOT EXISTS Main_DB;

Use Main_DB;


CREATE TABLE `Student` (
  `Student_ID` int NOT NULL,
  `F_Name` varchar(255),
  `M_initial` varchar(255),
  `L_Name` varchar(255),
  `Address` varchar(255),
  `School_Email` varchar(255),
  `Parent_ID` int,
  `Sex` varchar(255),
  `DOB` date,
  `Join_Date` date,
  
  PRIMARY KEY (`Student_ID`),
  FOREIGN KEY (`Parent_ID`) REFERENCES `Parents` (`Parent_ID`)
);

CREATE TABLE `Demerits` (
  `Dem_ID` int NOT NULL,
  `Student_ID` int,
  `Details` varchar(255),
  `Resolved` boolean,
  PRIMARY KEY (`Dem_ID`),
  FOREIGN KEY (`Student_ID`) REFERENCES `Student` (`Student_ID`)
);

CREATE TABLE `Parents` (
`Parent_ID` int NOT NULL,
`F_Name` varchar(255),
`M_Name` varchar(255),
`L_Name` varchar(255),
`Address` varchar(255),
PRIMARY KEY (`Parent_ID`)
);
-- ADDITIONAL TABLES (CB)

CREATE TABLE Teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100)
);
  CREATE TABLE Subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100),
    teacher_id INT,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id)
);
  CREATE TABLE Assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT,
    title VARCHAR(100),
    due_date DATE,
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id)
);
CREATE TABLE Results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    assignment_id INT,
    score INT,
    grade_letter CHAR(2),
    FOREIGN KEY (student_id) REFERENCES Student(Student_ID),
    FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id)
);
