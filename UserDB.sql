create database UserDB;

CREATE TABLE Users(
    user_id INT IDENTITY(1,1) PRIMARY KEY, 
    username VARCHAR(50) NOT NULL UNIQUE, 
    email VARCHAR(100) NOT NULL UNIQUE,  
    password_hash VARCHAR(255) NOT NULL
);


select * from Users


