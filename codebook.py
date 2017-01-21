#!/usr/local/bin/python2.7

import os
from codebook_mod import *
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    # render the home page
    return render_template('home.html', title='CODEBOOK')


@app.route('/register/', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pw1 = request.form['pw1']
        pw2 = request.form['pw2']
        if username == "" or pw1 == "" or pw2 == "":
            flash("One or more fields are empty.")
            return redirect(url_for('register'))
        result = signup(username,pw1,pw2)
        if result == 0:
            flash('The passwords do not match.')
            return redirect(url_for('register'))
        elif result == 1:
            flash('The username already exists.')
            return redirect(url_for('register'))
        else:
            session['username'] = username
            session['logged_in'] = True
            flash('The username ' + username + ' and password have been added!!!')
    return render_template('register.html', title='SIGN UP')


@app.route('/login/', methods=['POST', 'GET'])
def logIn():
    if 'username' in session:
        if request.method == 'POST':
            session.pop('username', None)
            session['logged_in'] = False
            flash('You are now logged out.')
            return render_template('login.html',title='Login | Logout',session=session)
        flash("You are logged in as " + session['username'] + ".")
        return render_template('login.html', title='Login | Logout', session=session)
    
    else:
        if request.method == 'POST':
            result = login(request.form['username'],request.form['password'])
            if result == 0:
                flash('Invalid username/password')
                return redirect(url_for('logIn'))
            if result == 1:
                flash('Successfully logged in as ' + request.form['username'] + '.')
                session['logged_in'] = True
                session['username'] = request.form['username']
                return redirect(url_for('bookmark'))
    return render_template('login.html', title='Login | Logout',session=session)


@app.route('/search/', methods=['POST','GET'])
def search():
    languages = listLanguages()
    if request.method == 'POST':
        if request.form['submit'] == 'Search':
            function_name = request.form['search-function']
            function_lang = request.form['language-name']
            if function_name == '' and function_lang == 'none': # when the user does not fill out the form
                flash('Please submit a non-blank form.')
                return redirect(url_for('search'))
            elif function_name and function_lang == 'none':
                results = searchName(function_name)
            elif function_lang and function_name == '':
                results = searchLang(function_lang)
            else:
                results = searchBoth(function_name, function_lang)

            if len(results) == 0:
                flash('There are no results.')
                return render_template('search.html', title='SEARCH CODEBOOK', languages=languages)
            else:
                return render_template('search.html', title='SEARCH CODEBOOK', languages=languages, results=results)
        else:
            if 'username' in session:
                username = session['username']
                addBookmark(username, request.form['submit'])
                flash("Bookmark has been added!")
                return redirect(url_for('search'))
            else:
                flash("Please login to add bookmarks.")
                return redirect(url_for('logIn'))
    return render_template('search.html',title="SEARCH CODEBOOK", languages=languages)


@app.route('/bookmarks/', methods=['GET','POST'])
def bookmark():
    if 'username' in session:
        username = session['username']
        results = listBookmarks(username)
        if request.method == 'POST':
            fid = request.form['submit']
            delBookmark(username, fid)
            flash(fid + " has been deleted from Bookmarks.")
            return redirect(url_for('bookmark'))
        else:            
            return render_template('bookmarks.html', title='BOOKMARKS', results=results)
    else:
        flash("Please login to view your bookmarks!")
        return redirect(url_for('logIn'))
    return render_template('bookmarks.html', title='BOOKMARKS')


@app.route('/add/', methods=['POST', 'GET'])
def add():
    languages = listLanguages()
    if request.method == 'POST':
        result = insert(request.form['function-language'],request.form['function-name'], request.form['function-description'],request.form['function-url'])
        if result == 1:
            message = 'The function has been added for approval.'
        else:
            message = 'That function already exists.'
        flash(message)
        return redirect(url_for('add'))
    return render_template('add.html', title='ADD FUNCTION', languages=languages)


@app.route('/pending/', methods=['POST', 'GET'])
def pending():
    if 'username' in session:
        if isAdmin(session['username']):
            pending = pendingFunctions()
            if request.method == 'POST':
                function_fid = request.form['function-fid']
                return redirect(url_for('approve', fid=function_fid))
            return render_template('pending.html', title='PENDING FUNCTIONS', isAdmin=isAdmin, functions=pending)
    flash("Only admins have access to this page.")
    return render_template('pending.html',title='PENDING FUNCTIONS', isAdmin=False)


@app.route('/approve/<fid>', methods=['POST', 'GET'])
def approve(fid):
    if 'username' in session and isAdmin(session['username']):
        function_info = search_fid(fid)
        if request.method == 'POST':
            if request.form['submit'] == 'approve': # when approve is clicked
                result = update(request.form['function-fid'],fid,request.form['function-name'],request.form['function-description'],request.form['function-url'],request.form['function-date']) # update the function in database
                if result == 1:
                    message = 'The function has been updated/approved.'
                else:
                    message = 'The new fid given is not unique. Cannot be updated/approved.'
                flash(message)

            else: # when delete is clicked
                result  = delete(fid) # delete function from database 
                if result == 1:
                    message = 'The function was successfully deleted.'
                else:
                    message = 'That function does not exist and cannot be deleted.'
                flash(message)
        
            return redirect(url_for('pending'))

        return render_template('approve.html', title='APPROVE FUNCTIONS', function_info=function_info, isAdmin=isAdmin)
    flash('Only admins have access to this page.')
    return render_template('approve.html',title='APPROVE FUNCTIONS', isAdmin=False)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())

