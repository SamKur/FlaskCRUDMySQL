-- run this once 

CREATE DATABASE if not exists flask_crud;

USE flask_crud;
drop table users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL CHECK (name <> ''),
    email VARCHAR(100) NOT NULL UNIQUE,
    age INT NOT NULL CHECK (age BETWEEN 0 AND 120)
);
