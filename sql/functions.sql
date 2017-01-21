-- For functions

use codebook_db;

drop table if exists bookmarks;
drop table if exists functions;

create table functions(
       fid varchar(20),
       name varchar(20),
       description varchar(50),
       url varchar(100),
       date_added date,
       status enum('approved','pending') default 'pending',
       INDEX(fid) 
       )
