from app import app
from flask import render_template, abort, request, redirect, url_for, flash
from app.functions import encrypt, decrypt
from flask_sqlalchemy import SQLAlchemy
import flask_login
import os

#  SQLAlchemy stuff
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'AWL.db')
app.secret_key = '56893655e2db25e3825b5bc259bb9032'
db.init_app(app)


#  Flask-WTForms stuff
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd' #  Think of a new secret key


#  Flask Login stuff
login_manager = flask_login.LoginManager()

login_manager.init_app(app)


from app.forms import Sign_Up, Log_In, Search_Bar
import app.models as models


#  Flask Login Methods
@login_manager.user_loader
def loader_user(user_id):
    return models.Users.query.get(user_id)


#  App Routes
@app.route('/')
def homepage():
    form = Search_Bar()
    return render_template('home.html', form = form)


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = Sign_Up()
    uniqueUser = None
    if request.method == 'GET': #  Render signup template first.
        return render_template('signup.html', form = form, title = 'Sign Up')
    else:
        if form.validate_on_submit(): #  if form validates on submit, do the following.
            new_user = models.Users()
            username = form.username.data
            password = encrypt(form.password.data)
            uniqueUser = new_user.query.filter_by(username = username).first() #  query any username in the database with the same name from the form data 'username'.
            if uniqueUser:
                flash('Already exists. Try again.')
                return render_template('signup.html', form = form, title = 'Sign Up')
            else:
                new_user.username = username
                new_user.password = password
                db.session.add(new_user)
                db.session.commit()
                flash(f'Welcome, { username }!')
                return redirect((url_for('homepage')))       


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = Log_In()
    if request.method == 'GET':
        return render_template('login.html', form = form, title = 'Log In')
    else:
        if form.validate_on_submit():
            user = models.Users.query.filter_by(
                username = form.username.data
            ).first()
            if user:
                if decrypt(user.password) == form.password.data:
                    flask_login.login_user(user)
                    flash(f'Long time no see, {user}!')
                    return(redirect(url_for('homepage')))
                else:
                    flash('Bad log in. Try again.')
                    return(redirect(request.url))
            else:
                flash('Bad log in. Try again.')
                return(redirect(request.url))


@app.route('/user_details')
def user_details():
    return render_template('user_details.html')


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
    form = Search_Bar()
    lower_word = str.lower(request.args.get('searching'))
    found = models.Words.query.filter_by(word = lower_word).first()
    if found: 
        return render_template('word_lookfor.html', word = found, form = form)
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