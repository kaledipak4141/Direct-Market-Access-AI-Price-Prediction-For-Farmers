
CREATE DATABASE IF NOT EXISTS farmer_table;
ALTER TABLE products ADD description TEXT;
USE farmer_table;
USE farmer_table;

ALTER TABLE products
ADD COLUMN description TEXT;
CREATE TABLE IF NOT EXISTS users(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
email VARCHAR(100),
password VARCHAR(100),
role VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS products(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
price INT,
ai_price INT,
image VARCHAR(255)
);

