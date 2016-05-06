# blog.py - controller

# imports
import sqlite3

from flask import g
from flask import Flask
from flask import flash
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import render_template
from functools import wraps


# configuration
DATABASE = 'blog.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = "_\xdbu'\x81\xa2\x06\x8d\x9d\x87H\x84\x94\x83S0E\xdbw\xf5\xa8\xce\xa0a"

app = Flask(__name__)

#pulls in app configuration by looking for UPPERCASE variables
app.config.from_object(__name__)


# function used for connection to the database
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for('login'))
    return wrap


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or \
           request.form['password'] != app.config['PASSWORD']:
           error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('main')) # because of def main():
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/main')
@login_required
def main():
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM posts')
    posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template('main.html', posts=posts)


@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    post = request.form['post']
    if not title or not post:
        flash('All fields are required. Please try again.')
        return redirect(url_for('main'))
    else:
        g.db = connect_db()
        g.db.execute('INSERT INTO posts (title, post) values (?, ?)',
                     [request.form['title'], request.form['post']])
        g.db.commit()
        g.db.close()
        flash('New entry was successfully posted!')
        return redirect('main')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)