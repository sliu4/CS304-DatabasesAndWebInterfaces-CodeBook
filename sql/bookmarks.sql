-- For bookmarks

use codebook_db;

drop table if exists bookmarks;

create table bookmarks (
       username varchar(50),
       fid varchar(20),
       INDEX(username),
       FOREIGN KEY (username) REFERENCES users (username),
       FOREIGN KEY (fid) REFERENCES functions (fid)
       )