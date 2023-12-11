CREATE DATABASE ktdb_dev CHARACTER SET utf8 COLLATE utf8_hungarian_ci;
CREATE USER IF NOT EXISTS ktadmin@'%' IDENTIFIED BY 'password';
GRANT ALL ON ktdb_dev.* TO ktadmin@'%';
GRANT ALL ON test_ktdb_dev.* TO ktadmin@'%';
FLUSH PRIVILEGES;
