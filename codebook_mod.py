#!/usr/local/bin/python2.7

# codebook_mod.py
# Sheree Liu and Hye Sun Yun

import uuid # for hashing password
import random # for hashing password
import hashlib # for hashing password
import MySQLdb
import dbconn2

def connect():
    '''Connects to the MySQL database using the dsn.cnf file and returns a cursor'''
    dsn = dbconn2.read_cnf('dsn.cnf')
    dsn['db'] = 'codebook_db'
    conn = dbconn2.connect(dsn)
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    return curs


def search_fid(fid):
    '''searches functions table with given fid and returns results'''
    curs = connect()
    curs.execute('SELECT * FROM functions WHERE fid=%s;',(fid,))
    row = curs.fetchone()
    return row


def searchName(function_name):
    '''searches the functions table based on the function name given. Returns all the functions that have the specified name.'''
    curs = connect()
    curs.execute('SELECT * FROM functions WHERE name like %s AND status="approved" ORDER BY fid ASC;',("%" + function_name + "%",))
    row = curs.fetchall()
    return row


def searchLang(lang):
    '''searches the function table for all the functions in that language.'''
    curs = connect()
    curs.execute('SELECT * FROM functions WHERE fid like %s AND status="approved" ORDER BY fid ASC;',(lang+"%",))
    row = curs.fetchall()
    return row


def searchBoth(function_name, lang):
    '''searches the function table for all functions in the given language with the given function name.'''
    curs = connect()
    curs.execute('SELECT * FROM functions WHERE fid like %s AND name like %s AND status="approved" ORDER BY fid ASC;', (lang+"%","%"+function_name+"%"))
    row = curs.fetchall()
    return row

   
def insert(lang, name, descrip, url):
    '''Inserts new function into function table with pending as default for status'''
    curs = connect()
    fid = lang + '_' + name
    row = search_fid(fid) # check if fid is unique
    if row == None: # fid is unique
        curs.execute('INSERT into functions VALUES (%s, %s, %s, %s, CURDATE(), DEFAULT);', (fid, name + '()', descrip, url))
        return 1
    else:
        return 0


def update(newfid, fid, name, descrip, url, date_added):
    '''Updates the function of the given fid with all the given criteria.'''
    # check if newfid is given and if it is unique!!
    curs = connect()
    row = search_fid(newfid) # check if newfid is unique
    if row == None or newfid == fid: # newfid is unique
        curs.execute('UPDATE functions SET fid=%s, name=%s, description=%s, url=%s, date_added=%s, status="approved" WHERE fid=%s;',(newfid, name, descrip, url, date_added, fid))
        return 1
    else:
        return 0


def pendingFunctions():
    '''Searches and returns all the functions in the functions table with the status as pending'''
    curs = connect()
    curs.execute('SELECT * FROM functions WHERE status="pending" ORDER BY fid ASC;')
    return curs.fetchall()


def delete(fid):
    '''deletes a row from the functions table using unique identifier fid'''
    curs = connect()
    row = search_fid(fid) # check if fid exists
    if row != None: # fid exists
        curs.execute('DELETE FROM functions WHERE fid=%s;',(fid,))
        return 1
    else:
        return 0

def listLanguages():
    '''lists all items in the languages table'''
    curs = connect()
    curs.execute('SELECT * FROM languages ORDER BY name;')
    row = curs.fetchall()
    return row


def listBookmarks(username):
    '''lists all the functions that are bookmarked by the given user'''
    curs = connect()
    curs.execute('SELECT functions.fid,url FROM bookmarks,functions WHERE username=%s AND bookmarks.fid=functions.fid ORDER BY functions.fid;',(username,))
    return curs.fetchall()


def addBookmark(username,fid):
    '''adds the function to the specified username to the bookmarks database table'''
    curs = connect()
    curs.execute('SELECT * FROM bookmarks WHERE username=%s AND fid=%s;',(username,fid))
    row = curs.fetchone()
    if row is None:
        curs.execute('INSERT into bookmarks VALUES (%s, %s);', (username, fid))
    else:
        return 0


def delBookmark(username,fid):
    '''deletes a bookmark from the user's bookmarks'''
    curs = connect()
    curs.execute('DELETE FROM bookmarks where username=%s AND fid=%s;',(username,fid))


def isAdmin(username):
    '''takes in a username and returns whether or not the username is an admin'''
    curs = connect()
    curs.execute('SELECT status FROM users WHERE username=%s;',(username,))
    row = curs.fetchone()
    return row['status'] == 'admin'


def hash_password(password):
    '''returns the hashed password with a random salt'''
    #uuid is used to generate a random number
    salt = (uuid.uuid4().hex)[:5]
    # hashedpw is the hashed password with the salt concatenated at the end
    hashedpw = hashlib.sha256(salt.encode()+password.encode()).hexdigest() + ':' + salt
    return hashedpw
   

def check_password(hashedpw,userpw):
    '''checks if the user input password is the same as the hashed password'''
    password, salt = hashedpw.split(':')
    return password == hashlib.sha256(salt.encode()+userpw.encode()).hexdigest()


def signup(username,pw1,pw2):
    '''signs up a user to the database'''
    curs = connect()
    hashedpw = hash_password(pw1)
    if check_password(hashedpw,pw2):
        curs.execute('SELECT * FROM users WHERE username=%s;', (username,))
        row = curs.fetchone()
        if row is None:
            curs.execute('INSERT into users VALUES (%s, %s, "regular", CURDATE());',(username,hashedpw))
        else:
            return 1 # when username is already in database
    else:
        return 0 # when the pw1 and pw2 do not match


def login(username,userpw):
    '''checks to make sure the given username and password matches the ones in the user database table'''
    curs = connect()
    # first checks if username exists in database
    curs.execute('SELECT password FROM users WHERE username=%s;',(username,))
    row = curs.fetchone()
    if row is None:
        return 0 # when username does not exist in database
    else:
       if check_password(row['password'],userpw):
           return 1 # username and password matched
       else:
           return 0 # username and password does not match
