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