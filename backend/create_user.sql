-- Run this in your MySQL database (e.g., via Workbench or CLI)
-- Replace 'newuser' and 'password' with your desired credentials.

CREATE USER 'newuser'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'newuser'@'%';
FLUSH PRIVILEGES;

-- If you only want to allow access from localhost:
-- CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
-- GRANT ALL PRIVILEGES ON *.* TO 'newuser'@'localhost';
