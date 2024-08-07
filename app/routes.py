from app import app
from flask import render_template, request, redirect, url_for, flash
from app.functions import encrypt, decrypt
from flask_sqlalchemy import SQLAlchemy
import flask_login
import os
from app.forms import Sign_Up, Log_In, Search_Bar
import random
import json


#  SQLAlchemy stuff
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'AWL.db')
app.secret_key = '56893655e2db25e3825b5bc259bb9032'
db.init_app(app)


#  Flask-WTForms stuff
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'  # Think of a new secret key


#  Flask Login stuff
login_manager = flask_login.LoginManager()

login_manager.init_app(app)


import app.models as models


#  Flask Login Methods
@login_manager.user_loader
def loader_user(user_id):
    return models.Users.query.get(user_id)


#  App Routes
@app.route('/')
def homepage():
    form = Search_Bar()
    return render_template('home.html', form=form)


@app.route('/nav')
def nav():
    return render_template('nav.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = Sign_Up()
    uniqueUser = None
    if request.method == 'GET':  # Render signup template first.
        return render_template('signup.html', form=form, title='Sign Up')
    else:
        if form.validate_on_submit():
            # if form validates on submit, do the following.
            new_user = models.Users()
            username = form.username.data
            password = encrypt(form.password.data)
            uniqueUser = new_user.query.filter_by(username=username).first()
            # query any username in the database with the
            # same name from the form data 'username'.
            if uniqueUser:
                flash('This user already exists. Try logging in.')
                return render_template('signup.html',
                                       form=form,
                                       title='Sign Up')
            else:
                new_user.username = username
                new_user.password = password
                db.session.add(new_user)
                db.session.commit()
                flash(f'Welcome, { username }!')
                return redirect(url_for('homepage'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Log_In()
    if request.method == 'GET':
        return render_template('login.html', form=form, title='Log In')
    else:
        if form.validate_on_submit():
            user = models.Users.query.filter_by(username=form.username.data).first()
            if user:
                if decrypt(user.password) == form.password.data:
                    flask_login.login_user(user)
                    flash(f'Long time no see, {user}!')
                    return redirect(url_for('homepage'))
                else:
                    flash('Bad log in. Try again.')
                    return redirect(request.url)
            else:
                flash('Bad log in. Try again.')
                return redirect(request.url)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('homepage'))


@app.route('/user_details')
def user_details():
    user = models.Users.query.filter_by(id=flask_login.current_user.get_id()).first()
    return render_template('user_details.html', user=user)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/sublist')
def all_words():
    return render_template('sublist.html')


@app.route('/sublist/words')
def sublist():
    words = models.Words.query.filter_by(sublist=1).all()
    return render_template('words.html', words=words)


@app.route('/sublist/words/<word>')
def word_listed(word):
    form = Search_Bar()
    word = models.Words.query.filter_by(word=word).first()
    next_word = models.Words.query.filter_by(id=word.id + 1).first()
    previous_word = models.Words.query.filter_by(id=word.id - 1).first()
    return render_template('word_listed.html',
                           form=form,
                           word=word,
                           next_word=next_word,
                           previous_word=previous_word)


@app.route('/sublist/words/lookfor', methods=['GET'])
def word_lookfor():
    form = Search_Bar()
    lower_word = str.lower(request.args.get('searching'))
    word = models.Words.query.filter_by(word=lower_word).first()
    if word:
        next_word = models.Words.query.filter_by(id=word.id + 1).first()
        previous_word = models.Words.query.filter_by(id=word.id - 1).first()
        return render_template('word_lookfor.html',
                               word=word,
                               form=form,
                               next_word=next_word,
                               previous_word=previous_word)
    else:
        flash('No such word.')
        return redirect(url_for('homepage'))


# AJAX request route
@app.route('/fill_request', methods=['POST'])
def fill_request():
    # takes 'correctItem' via the XMLHttpRequest
    json_item = request.get_json('correctItem')

    # if the current user is authenticated (they are logged in)
    if flask_login.current_user.is_authenticated is True:

        # get from database the column 'fill_progress'
        query = models.Users.query.filter_by(id=flask_login.current_user.id).first()

        # if 'query' is None (there are currently no tracked progress for this user)
        if not query.fill_progress:
            print('no progress found in the databse for this user!') #  DEBUG

            # initialize 'fill_progress'---the python list that will hold the
            # 'correctItem' value if it is not in the list yet
            fill_progress = []

        # if 'query' already exists
        else:
            print("this user's progress is tracked!") #  DEBUG

            # initializes 'fill_progress' as the parsed JSON list (which comes from
            # 'query', if it exists) containing the current progress of the user
            fill_progress = json.loads(query.fill_progress)

        # if 'fill_progress' is initialized as having nothing inside
        if not fill_progress:
            print('nothing in the list yet!') #  DEBUG

            # append to 'fill_progress' 'json_item' (since there is no tracked progress,
            # any progress is new progress)
            fill_progress.append(json_item)

            # converts 'fill_progress', a python list, into JSON
            for_adding = json.dumps(fill_progress)

            # equates 'query', the 'fill_progress' column in the database, to 'for_adding'
            query.fill_progress = for_adding
            db.session.commit()

        # if 'fill_progress' is initialized with values inside it
        else:
            print('list has something inside!') #  DEBUG

            # checks for new progress by not appending to 'fill_progress' the value of
            # 'json_item' that is found in the list
            if json_item not in fill_progress:
                    print('this is new progress!') #  DEBUG

                    # same process as above
                    fill_progress.append(json_item)
                    for_adding = json.dumps(fill_progress)
                    query.fill_progress = for_adding
                    db.session.commit()
            else:
                print('this is NOT new progress!')

    return ('From Python: Got it!')


# Quizzes
@app.route('/fill_in_the_blank', methods=['GET', 'POST'])
def fill_in_the_blank():
    sublist = request.form.get('sublist')
    random_forms = []
    if sublist:
        words = models.Words.query.filter_by(sublist=sublist).all()
        all_forms = []
        for word in words:
            add = [word.form[0],
                   word.form[1],
                   word.form[2]]
            all_forms.extend(add)

        # generate five random 'forms'
        random_forms = random.sample(all_forms, 5)

    return render_template('fill_in_the_blank.html',
                           sublist=sublist,
                           random_forms=random_forms)


@app.route('/form', methods=['GET'])
def form():
    sublist = request.args.get('sublist')

    # 'random_forms_main' is a nested list that will contain
    # 'random_forms_sublist'.
    random_forms_main = []
    random_blank_main = []
    random_blank_amount = 0

    if sublist:
        words = models.Words.query.filter_by(sublist=sublist).all()

        # generate five random word ids
        random_word_id = []
        for i in range(5):
            n = random.randint(1, 60)
            random_word_id.append(n)

        # for deciding which 'form' becomes blank
        random_blank_sublist = []
        for i in range(5):

            # generate a random integer between 1 and 2 that will
            # decide how many of the three forms will be left blank
            n = random.randint(1, 2)
            blanks = [0] * n
            random_blank_sublist.extend(blanks)
            not_blanks = [1] * (3 - n)
            random_blank_sublist.extend(not_blanks)
            random_blank_main.append(random_blank_sublist)
            random_blank_sublist = []

        # Count how many blank items will be generated
        for content in random_blank_main:
            for i in content:
                random_blank_amount += i

        # This list will be nested inside 'random_forms_main'
        random_forms_sublist = []

        # For every 'id' in 'random_word_id'...
        for i in random_word_id:

            # for every 'word' in 'words'...
            for word in words:

                # check if 'word.id' is equal to 'id'
                if word.id == i:

                    # add every form of the word into 'random_forms_sublist
                    add = [word.form[0],
                           word.form[1],
                           word.form[2]]
                    random_forms_sublist.extend(add)

                    # add 'random_forms_sublist' to '..._main'
                    random_forms_main.append(random_forms_sublist)

                    # remove the items in '..._sublist' and repeat
                    random_forms_sublist = []

    return render_template('form.html',
                           sublist=sublist,
                           random_forms_main=random_forms_main,
                           random_blank_main=random_blank_main,
                           random_blank_amount=random_blank_amount)


@app.route('/match', methods=['GET'])
def match():
    sublist = request.args.get('sublist')

    # holds the random words
    random_words = []

    # holds the definitions for the random words
    random_definitions = []

    # an array of 0's and 1's that will decide wether
    # a button will hold a 'word' or a 'definition'
    arrange = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]

    # shuffles the 'arrange' list before passing into template
    random.shuffle(arrange)

    if sublist:
        words = models.Words.query.filter_by(sublist=sublist).all()

        # uses random.sample to get 5 random words from 'words'
        random_words = random.sample(words, 5)

    for word in random_words:

        # takes the first definition of each 'word' in 'random_words'
        # and appends it to 'random_definitions'
        random_definitions.append(word.definition[0])

    return render_template('match.html',
                           sublist=sublist,
                           random_words=random_words,
                           random_definitions=random_definitions,
                           arrange=arrange)


@app.route('/question_answer', methods=['GET'])
def question_answer():
    sublist = request.args.get('sublist')
    words = []
    random_words = None
    question_type = None
    question_form_class = None

    if sublist:
        words = models.Words.query.filter_by(sublist=sublist).all()
        random_words = random.sample(words, 4)

        question_type = random.randint(1, 5)

        if question_type == 4:
            question_form_class = random.randint(1, 3)

    return render_template('question_answer.html',
                           sublist=sublist,
                           random_words=random_words,
                           question_type=question_type,
                           question_form_class=question_form_class)


@app.route('/quiz', methods=['GET'])
def quiz():
    sublist = request.args.get('sublist')
    words = []
    question_amount = 5

    if sublist:
        words = models.Words.query.filter_by(sublist=sublist).all()

    return render_template('quiz.html',
                           sublist=sublist,
                           words=words,
                           question_amount=question_amount)

# Custom Jinja filters


# Shuffle filter to shuffle elements in a list
@app.template_filter('shuffle')
def filter_shuffle(seq):
    result = list(seq)
    random.shuffle(result)
    return result


@app.template_filter('choice')
def filter_choice(seq):
    result = random.choice(seq)
    return result


# Context processor stuffs
@app.context_processor
# I can't make this into a filter because 'sample' needs
# two arguments. Instead, I used context processor
def sample():
    # '_sample' function inside 'sample' which needs two
    # arguments, 'seq' for the list and 'amount' for the
    # amount of items to be sampled
    def _sample(seq, amount):
        result = random.sample(seq, amount)
        # internally returns 'result'
        return result
    # ultimately returns 'sample' as the returned value of
    # '_sample' using 'dict'
    return dict(sample=_sample)


if __name__ == '__main__':
    app.run(debug=True)
