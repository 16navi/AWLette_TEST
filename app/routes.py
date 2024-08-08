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
@app.route('/progress_tracker', methods=['POST'])
def progress_tracker():
    # get the posted dictionary
    posted_dict = request.get_json()

    # assign necessary values
    sublist, quiz_type, correct_id, quiz_progress, selected_tracker = None, None, None, None, None
    dict_values, dict_keys, correct_list = [], [], []
    for key, value in posted_dict['correctItem'].items():
        dict_keys.append(key)
        dict_values.append(value)

    correct_id = int(dict_values[0])
    sublist = int(dict_values[1])
    quiz_type = dict_keys[0]

    progress_dict = {
        sublist: correct_list
    }

    if flask_login.current_user.is_authenticated is True:
        tracker = models.ProgTrack.query.filter_by(users_id=flask_login.current_user.id).all()
        new_tracker = models.ProgTrack()

        # look for any progress for a specific type of quiz---meaning, look
        # for a row where a specific column is not null

        if not tracker:
            print('\nuser has no recorded progress in everything!\n')  # DEBUG
            new_tracker.users_id = flask_login.current_user.id
            db.session.add(new_tracker)
            db.session.commit()

            # for fill quizzes
            if quiz_type == 'fill':
                # Now that user exists in 'ProgTrack', we will query for user
                user = models.ProgTrack.query.filter_by(users_id=flask_login.current_user.id).first()
                correct_list.append(correct_id)
                user.fill_progress = json.dumps(progress_dict)
                db.session.commit()

            # for form quizzes
            if quiz_type == 'form':
                # Now that user exists in 'ProgTrack', we will query for user
                user = models.ProgTrack.query.filter_by(users_id=flask_login.current_user.id).first()
                correct_list.append(correct_id)
                user.form_progress = json.dumps(progress_dict)
                db.session.commit()

            # for match quizzes
            if quiz_type == 'match':
                # Now that user exists in 'ProgTrack', we will query for user
                user = models.ProgTrack.query.filter_by(users_id=flask_login.current_user.id).first()
                correct_list.append(correct_id)
                user.match_progress = json.dumps(progress_dict)
                db.session.commit()

            # for qna quizzes
            if quiz_type == 'qna':
                # Now that user exists in 'ProgTrack', we will query for user
                user = models.ProgTrack.query.filter_by(users_id=flask_login.current_user.id).first()
                correct_list.append(correct_id)
                user.qna_progress = json.dumps(progress_dict)
                db.session.commit()

        else:
            for i in reversed(tracker):
                if quiz_type == 'fill':
                    if i.fill_progress is not None:
                        quiz_progress = True
                    else:
                        quiz_progress = False

                if quiz_type == 'form':
                    if i.form_progress is not None:
                        quiz_progress = True
                    else:
                        quiz_progress = False

                if quiz_type == 'match':
                    if i.form_progress is not None:
                        quiz_progress = True
                    else:
                        quiz_progress = False

                if quiz_type == 'qna':
                    if i.qna_progress is not None:
                        quiz_progress = True
                    else:
                        quiz_progress = False
        
        if quiz_progress is True:
            if quiz_type == 'fill':
                print('\nthere is progress for fill!\n')  # DEBUG
                loop_index = -1
                found_index = None

                # for each row in the database in 'tracker'
                for row in tracker:
                    loop_index += 1
                    # initialize variables for iteration
                    row_key = None
                    row_value = None

                    # for key, value in pythonified 'fill_progress' which is a dict
                    if row.fill_progress:
                        for key, value in json.loads(row.fill_progress).items():
                            row_key = key
                            row_value = value

                        # if 'sublist' is the same as the 'row_key'
                        if str(sublist) == row_key:
                            print(f'\nfound tracker for sublist no. {sublist}!')  # DEBUG
                            found_index = loop_index

                            # get the 'row_value' which contains the 'correct_list'
                            correct_list = row_value
                            print(f'correct_list now has value: {correct_list}!\ncorrect_id will be added to this list shortly after...\n')  # DEBUG

                # if 'correct_list' is still empty, that means we found no tracker for
                # this sublist
                if not correct_list:
                    print(f'\nno tracker for sublist no. {sublist}...\n')  # DEBUG
                    selected_tracker = new_tracker
                    selected_tracker.users_id = flask_login.current_user.id

                    for i in tracker:
                        if i.fill_progress is None:
                            selected_tracker = i

                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                        }
                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')

                    selected_tracker.fill_progress = json.dumps(progress_dict)
                    db.session.add(selected_tracker)
                    db.session.commit()

                elif correct_list:
                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                    }

                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')
                    found_tracker = tracker[found_index]
                    found_tracker.fill_progress = json.dumps(progress_dict)
                    db.session.commit()

                elif correct_list:
                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                    }

                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')
                    found_tracker = tracker[found_index]
                    found_tracker.fill_progress = json.dumps(progress_dict)
                    db.session.commit()

            if quiz_type == 'form':
                print('\nthere is progress for form!\n')  # DEBUG
                loop_index = -1
                found_index = None

                # for each row in the database in 'tracker'
                for row in tracker:
                    loop_index += 1
                    # initialize variables for iteration
                    row_key = None
                    row_value = None

                    # for key, value in pythonified 'form_progress' which is a dict
                    if row.form_progress:
                        for key, value in json.loads(row.form_progress).items():
                            row_key = key
                            row_value = value

                            # if 'sublist' is the same as the 'row_key'
                            if str(sublist) == row_key:
                                print(f'\nfound tracker for sublist no. {sublist}!')  # DEBUG
                                found_index = loop_index

                                # get the 'row_value' which contains the 'correct_list'
                                correct_list = row_value
                                print(f'correct_list now has value: {correct_list}!\ncorrect_id will be added to this list shortly after...\n')  # DEBUG

                # if 'correct_list' is still empty, that means we found no tracker for
                # this sublist
                if not correct_list:
                    print(f'\nno tracker for sublist no. {sublist}...\n')  # DEBUG
                    selected_tracker = new_tracker
                    selected_tracker.users_id = flask_login.current_user.id

                    for i in tracker:
                        if i.form_progress is None:
                            selected_tracker = i

                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                        }
                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')

                    selected_tracker.form_progress = json.dumps(progress_dict)
                    db.session.add(selected_tracker)
                    db.session.commit()

                elif correct_list:
                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                    }

                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')
                    found_tracker = tracker[found_index]
                    found_tracker.form_progress = json.dumps(progress_dict)
                    db.session.commit()

            if quiz_type == 'match':
                print('\nthere is progress for match!\n')  # DEBUG
                loop_index = -1
                found_index = None

                # for each row in the database in 'tracker'
                for row in tracker:
                    loop_index += 1
                    # initialize variables for iteration
                    row_key = None
                    row_value = None

                    # for key, value in pythonified 'match_progress' which is a dict
                    if row.match_progress:
                        for key, value in json.loads(row.match_progress).items():
                            row_key = key
                            row_value = value

                        # if 'sublist' is the same as the 'row_key'
                        if str(sublist) == row_key:
                            print(f'\nfound tracker for sublist no. {sublist}!')  # DEBUG
                            found_index = loop_index

                            # get the 'row_value' which contains the 'correct_list'
                            correct_list = row_value
                            print(f'correct_list now has value: {correct_list}!\ncorrect_id will be added to this list shortly after...\n')  # DEBUG

                # if 'correct_list' is still empty, that means we found no tracker for
                # this sublist
                if not correct_list:
                    print(f'\nno tracker for sublist no. {sublist}...\n')  # DEBUG
                    selected_tracker = new_tracker
                    selected_tracker.users_id = flask_login.current_user.id

                    for i in tracker:
                        if i.match_progress is None:
                            selected_tracker = i

                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                        }
                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')

                    selected_tracker.match_progress = json.dumps(progress_dict)
                    db.session.add(selected_tracker)
                    db.session.commit()

                elif correct_list:
                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                    }

                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')
                    found_tracker = tracker[found_index]
                    found_tracker.match_progress = json.dumps(progress_dict)
                    db.session.commit()

            if quiz_type == 'qna':
                print('\nthere is progress for qna!\n')  # DEBUG
                loop_index = -1
                found_index = None

                # for each row in the database in 'tracker'
                for row in tracker:
                    loop_index += 1
                    # initialize variables for iteration
                    row_key = None
                    row_value = None

                    # for key, value in pythonified 'qna_progress' which is a dict
                    if row.qna_progress:
                        for key, value in json.loads(row.qna_progress).items():
                            row_key = key
                            row_value = value

                        # if 'sublist' is the same as the 'row_key'
                        if str(sublist) == row_key:
                            print(f'\nfound tracker for sublist no. {sublist}!')  # DEBUG
                            found_index = loop_index

                            # get the 'row_value' which contains the 'correct_list'
                            correct_list = row_value
                            print(f'correct_list now has value: {correct_list}!\ncorrect_id will be added to this list shortly after...\n')  # DEBUG

                # if 'correct_list' is still empty, that means we found no tracker for
                # this sublist
                if not correct_list:
                    print(f'\nno tracker for sublist no. {sublist}...\n')  # DEBUG
                    selected_tracker = new_tracker
                    selected_tracker.users_id = flask_login.current_user.id

                    for i in tracker:
                        if i.qna_progress is None:
                            selected_tracker = i

                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                        }
                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')

                    selected_tracker.qna_progress = json.dumps(progress_dict)
                    db.session.add(selected_tracker)
                    db.session.commit()

                elif correct_list:
                    if correct_id not in correct_list:
                        correct_list.append(correct_id)

                    progress_dict = {
                        sublist: correct_list
                    }

                    print(f'\nprogress_dict is now --{progress_dict}-- adding to database...\n')
                    found_tracker = tracker[found_index]
                    found_tracker.qna_progress = json.dumps(progress_dict)
                    db.session.commit()

        if quiz_progress is False:
            if quiz_type == 'fill':
                print('\nthere is NO progress for fill!\n')  # DEBUG
                for i in tracker:
                    if i.fill_progress is None:
                        selected_tracker = i
                correct_list.append(correct_id)
                selected_tracker.fill_progress = json.dumps(progress_dict)
                db.session.commit()

            if quiz_type == 'form':
                print('\nthere is NO progress for form!\n')  # DEBUG
                for i in tracker:
                    if i.form_progress is None:
                        selected_tracker = i
                correct_list.append(correct_id)
                selected_tracker.form_progress = json.dumps(progress_dict)
                db.session.commit()

            if quiz_type == 'match':
                print('\nthere is NO progress for match!\n')  # DEBUG
                for i in tracker:
                    if i.match_progress is None:
                        selected_tracker = i
                correct_list.append(correct_id)
                selected_tracker.match_progress = json.dumps(progress_dict)
                db.session.commit()

            if quiz_type == 'qna':
                print('\nthere is NO progress for qna!\n')  # DEBUG
                for i in tracker:
                    if i.qna_progress is None:
                        selected_tracker = i
                correct_list.append(correct_id)
                selected_tracker.qna_progress = json.dumps(progress_dict)
                db.session.commit()

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

        # sample five random words
        random_words = random.sample(words, 5)

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
        for word in random_words:

            # add every form of the word into 'random_forms_sublist'
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
    # random_definitions = []

    # an array of 0's and 1's that will decide wether
    # a button will hold a 'word' or a 'definition'
    arrange = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]

    # shuffles the 'arrange' list before passing into template
    random.shuffle(arrange)

    if sublist:
        words = models.Words.query.filter_by(sublist=sublist).all()

        # uses random.sample to get 5 random words from 'words'
        random_words = random.sample(words, 5)

    return render_template('match.html',
                           sublist=sublist,
                           random_words=random_words,
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
