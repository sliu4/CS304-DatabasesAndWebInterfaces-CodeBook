-- For languages

use codebook_db;

drop table if exists languages;

create table languages (
       name varchar(20),
       abbreviation varchar(20),
       INDEX(name)
       )