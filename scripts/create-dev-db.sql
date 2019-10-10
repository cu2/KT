CREATE DATABASE ktdb_dev CHARACTER SET utf8 COLLATE utf8_hungarian_ci;
GRANT ALL ON ktdb_dev.* TO ktadmin@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
