#ALL IMPORTS

import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
       abort, render_template, flash
from contextlib import closing

# MY BLOG APP
app = Flask(__name__)

app.config.from_envvar('FLASKBLOG_SETTINGS', silent=True)

# Connect's to our db and returns a dict
def connect_db():
    rv = sqlite3.connect('DATABASE')
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# INDEX PAGE
@app.route('/')
def show_entries():
    cur = g.db.execute('SELECT title, text FROM entries ORDER BY id DESC')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries )

# ADD NEW ENTRY
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)

    g.db.execute('INSERT INTO entries (title, text) VALUES (?,?)',
            [request.form['title'], request.form['text']])
    g.db.commit()

    flash('New entry successfully added')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


#Error Logging for production

#Mail
ADMINS = ['jelianchaszer@gmail.com']

if not app.debug:
    import logging
    from logging import Formatter
    from logging.handlers import SMTPHandler, RotatingFileHandler 
    mail_handler = SMTPHandler('127.0.0.1',
                                'flask-blog-server-error@myblog.com',
                                ADMINS, 'Flask Blog Encountered an error')

    err_format = Formatter('''
        Message type:   %(levelname)s
        Location:       %(pathname)s: %(lineno)d
        Module:         %(module)s
        Function:       %(funcName)s
        Time:           %(asctime)s

        Message:

            %(message)s
    ''')

    file_handler = RotatingFileHandler('error_log.log', maxBytes=10000000, backupCount=1)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(err_format)
    app.logger.addHandler(file_handler)

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(err_format)
    app.logger.addHandler(mail_handler)



if __name__ == '__main__':
    app.run(debug=True)
