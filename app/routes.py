from app import app
from flask import render_template, abort, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

#  SQLAlchemy stuff
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'AWL.db')
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'
db.init_app(app)


#  Flask-WTForms stuff
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd' #  Think of a new secret key


from app.forms import Sign_Up
import app.models as models


def searchWord(lookfor, wordlist):
    found = -1
    for word in wordlist:
        if str.lower(lookfor) == str(word):
            found = word
    return found

def uniqueUser(user, user_list):
    for i in user_list:
        if user == i:
            return False


@app.route('/')
def homepage():
    wordlist = models.Words.query.all()
    search = None
    result = -1
    if len(request.args) == None:
        print('No word typed.')  # DEBUG
    if len(request.args) > 0:
        search = request.args.get('searching')
        result = searchWord(search, wordlist)
    return render_template('home.html', result = result)

# Our goal for this branch is to create a 
# sign-up and log-in feature for students.
# This will help for progress tracking, which
# I do not know how to even start doing.

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = Sign_Up()
    if request.method == 'GET':
        return render_template('signup.html', form = form, title = 'Sign Up')
    else:
        if form.validate_on_submit():
            new_user = models.Users()
            user_list = models.Users.query.all()
            new_user.username = form.username.data
            new_user.password = form.password.data
            db.session.add(new_user)
            db.session.commit()
            #  Find a way to keep username and password unique,
            #  preferably inside forms.py so as to use ValidationError
            flash(f'Welcome {form.username.data}!')
            return redirect((url_for('homepage')))
        else:
            return render_template('signup.html', form = form, title = 'Sign Up')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/sublist')
def all_words():
    return render_template('sublist.html')


@app.route('/sublist/words')
def sublist():
    words = models.Words.query.filter_by(sublist = 1).all()
    return render_template('words.html', words = words)


@app.route('/sublist/words/<word>')
def word_listed(word):
    listed = models.Words.query.filter_by(word = word).one()
    return render_template('word_listed.html', word = listed)


@app.route('/sublist/words/lookfor', methods = ['GET'])
def word_lookfor():
    lower_word = str.lower(request.args.get('searching'))
    found = models.Words.query.filter_by(word = lower_word).first()
    if found: 
        return render_template('word_lookfor.html', word = found)
    else:
        flash('No such word.')
        return redirect((url_for('homepage')))


@app.route('/fill_in_the_blank')
def fill_in_the_blank():
    return render_template('fill_in_the_blank.html')


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/match')
def match():
    return render_template('match.html')


@app.route('/question_answer')
def question_answer():
    return render_template('question_answer.html')


@app.route('/quiz')
def quiz():
    return render_template('quiz.html')


if __name__ == '__main__':
    app.run(debug=True)