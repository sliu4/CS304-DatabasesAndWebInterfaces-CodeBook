-- User table for codebook

use codebook_db;

drop table if exists bookmarks;
drop table if exists users;


create table users (
       username varchar(50),
       password varchar(50),
       status enum('regular','admin'),
       date_created date,
       INDEX(username) 
       ) ENGINE = INNODB;
    