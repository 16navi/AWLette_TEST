from app import app
from flask import render_template, request, redirect, url_for, flash
from app.functions import encrypt, decrypt, generate_code
from flask_sqlalchemy import SQLAlchemy
import flask_login
import os
from app.forms import Sign_Up, Log_In, Search_Bar, Create_Classroom, Enrol, Create_Quiz
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


user = flask_login.current_user


#  App Routes
@app.route('/')
def homepage():
    form = Search_Bar()
    if not user.is_anonymous and user.is_teacher == 1:
        classrooms = models.Classrooms.query.filter_by(teacher_id=user.id,
                                                       is_disabled=None).all()
        return render_template('home.html', form=form, classrooms=classrooms)
    else:
        return render_template('home.html', form=form)


# Admin login
# admin credentials: (Admin ,G1SJso3zIio)
@app.route('/admin_powers')
def admin_powers():
    if user.is_authenticated:
        if user.is_admin:
            return render_template('admin.html')
        else:
            flash(f"You're not Admin, are you, {user}?")
            return redirect(url_for('homepage'))
    else:
        flash('How about logging in first?')
        return redirect(url_for('homepage'))


@app.route('/admin_powers/disable_account')
def disable_account():
    if not user.is_admin:
        flash(f"You're not Admin, are you, {user}?")
        return redirect(url_for('homepage'))
    else:
        users = models.Users.query.filter_by(is_admin=None).all()
        return render_template('admin_disable_acc.html', users=users)


# Account disabler AJAX route
@app.route('/account_disabler', methods=['POST'])
def account_disabler():
    posted_dict = request.get_json()

    dict_key, dict_value = None, None
    for key, value in posted_dict['disableDict'].items():
        dict_key, dict_value = key, value

    account = models.Users.query.filter_by(id=int(dict_value)).first()

    if dict_key == 'disable':
        account.is_disabled = 1
        db.session.commit()
    else:
        account.is_disabled = None
        db.session.commit()

    return ('From Python: Got it!')


@app.route('/admin_powers/disable_classroom')
def disable_classroom():
    if not user.is_admin:
        flash(f"You're not Admin, are you, {user}?")
        return redirect(url_for('homepage'))
    else:
        classrooms = models.Classrooms.query.all()
        return render_template('admin_disable_classroom.html', classrooms=classrooms)


# Classroom disabler AJAX route
@app.route('/classroom_disabler', methods=['POST'])
def classroom_disabler():
    posted_dict = request.get_json()

    dict_key, dict_value = None, None
    for key, value in posted_dict['disableDict'].items():
        dict_key, dict_value = key, value

    classroom = models.Classrooms.query.filter_by(id=int(dict_value)).first()

    if dict_key == 'disable':
        classroom.is_disabled = 1
        db.session.commit()
    else:
        classroom.is_disabled = None
        db.session.commit()

    return ('From Python: Got it!')


# Teacher request AJAX route
@app.route('/grant_or_reject', methods=['POST'])
def grant_or_reject():
    posted_dict = request.get_json()
    action, id = None, None
    for key, value in posted_dict.items():
        action = key
        id = value

    if action == 'grant':
        print(f'Admin granted user id {id} the role of teacher!')  # DEBUG
        teacher = models.Users.query.filter_by(id=id).first()
        teacher.is_teacher = 1
        db.session.commit()

    if action == 'reject':
        print(f'Admin rejected the request of user id {id} for the role of teacher!')  # DEBUG
        teacher = models.Users.query.filter_by(id=id).first()
        teacher.is_teacher = None
        db.session.commit()

    return ('From Python: Got it!')


@app.route('/admin_powers/teacher_request')
def teacher_request():
    requesting_teachers = models.Users.query.filter_by(is_teacher=0).all()
    return render_template('teacher_request.html',
                           requesting_teachers=requesting_teachers)


@app.route('/create_classroom', methods=['GET', 'POST'])
def create_classroom():
    if user.is_authenticated:
        if user.is_teacher == 1:
            form = Create_Classroom()
            if request.method == 'GET':
                return render_template('create_classroom.html',
                                       form=form)
            else:
                if form.validate_on_submit():
                    new_classroom = models.Classrooms()
                    new_classroom.classroom = form.classroom_name.data
                    new_classroom.description = form.description.data
                    unique_code = None
                    # Check if code is unique by querying database for classrooms
                    # with the code
                    while not unique_code:
                        code = generate_code(3)
                        query = models.Classrooms.query.filter_by(code=code).first()
                        if not query:
                            unique_code = code
                    new_classroom.code = unique_code
                    new_classroom.teacher_id = user.id
                    db.session.add(new_classroom)
                    db.session.commit()
                    return redirect(url_for('homepage'))
        else:
            flash(f"You're not a teacher, are you, {user}?")
            return redirect(url_for('homepage'))
    else:
        flash('How about logging in first?')
        return redirect(url_for('homepage'))


@app.route('/classroom/<classroom_id>')
def classroom_stream(classroom_id):
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    quizzes = models.Quiz.query.filter_by(classroom_id=classroom_id).all()
    if classroom.is_disabled:
        flash(f'Classroom {classroom} is disabled.')
        return redirect(url_for('homepage'))
    elif user.is_anonymous:
        flash('How about logging in first?')
        return redirect(url_for('homepage'))
    elif user.is_teacher == 1:
        return render_template('classroom_stream.html', classroom=classroom, quizzes=quizzes)
    else:
        if user in classroom.student:
            taken_quiz = models.UserQuiz.query.filter_by(users_id=user.id).all()
            if taken_quiz:
                for quiz in taken_quiz:
                    quizzes.remove(quiz.quiz)
            for quiz in quizzes:
                if quiz.is_archived:
                    quizzes.remove(quiz)
            return render_template('classroom_stream.html', classroom=classroom, quizzes=quizzes)
        else:
            flash(f"You're not in this classroom, are you, {user}?")
            return redirect(url_for('homepage'))


# Quiz Archive AJAX Route
@app.route('/quiz_archiver', methods=['POST'])
def quiz_archiver():
    posted_dict = request.get_json()
    dict_value, dict_key = None, None
    for key, value in posted_dict['archiveDict'].items():
        dict_value = int(value)
        dict_key = key

    quiz = models.Quiz.query.filter_by(id=dict_value).first()

    if dict_key == 'archive':
        quiz.is_archived = 1
        db.session.commit()
    else:
        quiz.is_archived = None
        db.session.commit()

    return ('From Python: Got it!')


@app.route('/classroom/<classroom_id>/create_quiz', methods=['GET', 'POST'])
def create_quiz(classroom_id):
    form = Create_Quiz()
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    if request.method == 'GET':
        sublist = request.args.get('sublist')
        words = models.Words.query.filter_by(sublist=sublist).all()
        return render_template('create_quiz.html', form=form, sublist=sublist, words=words, classroom=classroom)
    else:
        if form.validate_on_submit():
            new_quiz = models.Quiz()
            new_quiz.name = form.name.data
            new_quiz.classroom_id = classroom_id
            new_quiz.item = form.item.data
            new_quiz.question_types = json.dumps(form.question_type.data)
            new_quiz.word_pool = form.word_pool.data
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz successfully created!')
            return redirect(url_for('classroom_stream', classroom_id=classroom_id))


@app.route('/classroom/<classroom_id>/custom_quiz/<quiz_id>')
def custom_quiz(classroom_id, quiz_id):
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    if user not in classroom.student:
        flash(f'This quiz is not for you, {user}.')
        return redirect(url_for('classroom_listed', classroom_id=classroom_id))
    quiz = models.Quiz.query.filter_by(id=quiz_id).first()
    words = []
    for id in json.loads(quiz.word_pool):
        words.append(models.Words.query.filter_by(id=id).first())
    question_amount = quiz.item
    types = json.loads(quiz.question_types)
    return render_template('custom_quiz.html',
                           quiz=quiz,
                           words=words,
                           question_amount=question_amount,
                           types=types,
                           classroom_id=classroom_id)


@app.route('/classroom/<classroom_id>/custom_quiz_progress/<quiz_id>')
def custom_quiz_progress(classroom_id, quiz_id):
    trackers = models.UserQuiz.query.filter_by(quiz_id=quiz_id).all()
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    not_answered = classroom.student
    for tracker in trackers:
        not_answered.remove(tracker.student)

    return render_template('custom_quiz_progress.html',
                           trackers=trackers,
                           not_answered=not_answered,
                           classroom=classroom)


# Custom Quiz AJAX
@app.route('/custom_quiz_tracker', methods=['POST'])
def custom_quiz_tracker():
    posted_dict = request.get_json()
    dict_values = []
    for key, value in posted_dict['correctItem'].items():
        dict_values.append(value)
    quiz_id = dict_values[0]
    correct_list = []
    for i in dict_values[1]:
        correct_list.append(int(i))
    user_id = dict_values[2]

    if not correct_list:
        return ("From Python: There are no correct id's received!")

    tracker_exists = models.UserQuiz.query.filter_by(users_id=user_id,
                                                     quiz_id=quiz_id).first()

    if not tracker_exists:
        quiz = models.Quiz.query.filter_by(id=quiz_id).first()
        quizzee = models.Users.query.filter_by(id=user_id).first()
        quizzee.finished_quiz.append(quiz)
        quiz.student.append(quizzee)
        db.session.commit()
    else:
        return ('From Python: User has already done this quiz!')

    quiz_tracker = models.UserQuiz.query.filter_by(users_id=user_id,
                                                   quiz_id=quiz_id).first()

    quiz_tracker.score = json.dumps(correct_list)
    db.session.commit()

    return ('From Python: Got it!')


@app.route('/classroom/<classroom_id>/people')
def people(classroom_id):
    if user.is_authenticated:
        classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
        teacher = models.Users.query.filter_by(id=classroom.teacher_id).first()
        return render_template('people.html',
                               classroom=classroom,
                               teacher=teacher)
    else:
        flash('How about logging in first?')
        return redirect(url_for('homepage'))


@app.route('/classroom/<classroom_id>/people/<users_id>')
def student_progress(classroom_id, users_id):
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    if user.is_teacher == 1:
        student = models.Users.query.filter_by(id=users_id).first()
        return render_template('student_progress.html', student=student, classroom=classroom)
    elif user.is_authenticated and user.is_teacher != 1:
        flash(f"You're not a teacher, are you, {user}?")
        return redirect(url_for('homepage'))


# @app.route('/classroom/<classroom_id>/leaderboards')
# def leaderboards(classroom_id):
#     if user.is_authenticated:
#         classroom = models.Classrooms.query.filter_by(id=classroom_id).first()

#         def count_progress(list, total):
#             if list:
#                 score = round(((len(list) / total) * 100), 2)
#                 return score
#             else:
#                 return None

#         return render_template('leaderboards.html', classroom=classroom)
#     else:
#         flash('How about logging in first?')
#         return redirect(url_for('homepage'))


@app.route('/enrol', methods=['GET', 'POST'])
def enrol():
    if user.is_authenticated:
        form = Enrol()
        if request.method == 'GET':
            return render_template('enrol.html', form=form)
        else:
            if form.validate_on_submit():
                code = form.code.data
                classroom = models.Classrooms.query.filter_by(code=code).first()
                if not classroom:
                    flash('Wrong code. Try again.')
                    return redirect(request.url)
                else:
                    user.enrolment.append(classroom)
                    classroom.student.append(user)
                    db.session.commit()
                    flash(f'Welcome to Classroom {classroom}, {user}!')
                    return redirect(url_for('homepage'))
    else:
        flash('How about logging in first?')
        return redirect(url_for('homepage'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not user.is_authenticated:
        form = Sign_Up()
        unique_user = None
        if request.method == 'GET':  # Render signup template first.
            return render_template('signup.html',
                                   form=form)
        else:
            if form.validate_on_submit():
                # if form validates on submit, do the following.
                new_user = models.Users()
                username = form.username.data
                password = encrypt(form.password.data)
                unique_user = new_user.query.filter_by(username=username).first()
                # query any username in the database with the
                # same name from the form data 'username'.
                if unique_user:
                    flash('This user already exists. Try logging in.')
                    return render_template('signup.html',
                                           form=form)
                else:
                    new_user.username = username
                    new_user.password = password
                    if form.is_teacher.data:
                        new_user.is_teacher = 0
                    db.session.add(new_user)
                    db.session.commit()
                    flask_login.login_user(new_user)
                    flash(f'Welcome, { username }!')
                    return redirect(url_for('homepage'))
    else:
        flash(f"You're already logged in, {user}!")
        return redirect(url_for('homepage'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not user.is_authenticated:
        form = Log_In()
        if request.method == 'GET':
            return render_template('login.html',
                                   form=form)
        else:
            if form.validate_on_submit():
                login_user = models.Users.query.filter_by(username=form.username.data).first()
                if login_user:
                    if not login_user.is_disabled:
                        if decrypt(login_user.password) == form.password.data:
                            flask_login.login_user(login_user)
                            if not login_user.is_admin:
                                flash(f'Long time no see, {login_user}!')
                                return redirect(url_for('homepage'))
                            else:
                                flash('Howdy, Admin!')
                                return redirect(url_for('homepage'))
                        else:
                            flash('Bad log in. Try again.')
                            return redirect(request.url)
                    else:
                        flash('Bad log in. Try again.')
                        return redirect(request.url)
                else:
                    flash('Bad log in. Try again.')
                    return redirect(request.url)
    else:
        flash(f"You're already logged in, {user}!")
        return redirect(url_for('homepage'))


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('homepage'))


@app.route('/user_details')
def user_details():
    if user.is_authenticated:
        return render_template('user_details.html')
    else:
        flash('How about logging in first?')
        return redirect(url_for('homepage'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/sublist')
def all_words():
    words = models.Words.query.all()
    return render_template('sublist.html', words=words)


@app.route('/sublist/<sublist>')
def sublist(sublist):
    words = models.Words.query.filter_by(sublist=sublist).all()
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


# AJAX request route for quizzes
@app.route('/progress_tracker', methods=['POST'])
def progress_tracker():
    # get the posted dictionary
    posted_dict = request.get_json()

    # assign necessary values
    sublist, quiz_type = None, None
    dict_values, dict_keys, correct_list, correct_id = [], [], [], []
    for key, value in posted_dict['correctItem'].items():
        dict_keys.append(key)
        dict_values.append(value)

    sublist = int(dict_values[1])
    quiz_type = dict_keys[0]

    if quiz_type != 'quiz':
        correct_id = int(dict_values[0])
    else:
        for i in dict_values[0]:
            if i != 0:
                correct_id.append(int(i))

    if user.is_authenticated is True:
        tracker = models.ProgTrack.query.filter_by(
            users_id=user.id,
            sublist=sublist).first()
        new_tracker = models.ProgTrack()

        if not tracker:
            print('\nuser has no recorded progress for any quiz in this sublist!\n')  # DEBUG
            new_tracker.users_id = user.id
            new_tracker.sublist = sublist
            db.session.add(new_tracker)
            db.session.commit()

            tracker = models.ProgTrack.query.filter_by(users_id=user.id,
                                                       sublist=sublist).first()

            if quiz_type != 'quiz':
                correct_list.append(correct_id)
            else:
                correct_list.extend(correct_id)
                tracker.quiz_progress = json.dumps(correct_list)

            if quiz_type == 'fill':
                tracker.fill_progress = json.dumps(correct_list)
            if quiz_type == 'form':
                tracker.form_progress = json.dumps(correct_list)
            if quiz_type == 'match':
                tracker.match_progress = json.dumps(correct_list)
            if quiz_type == 'qna':
                tracker.qna_progress = json.dumps(correct_list)

            db.session.commit()

        else:
            tracker = models.ProgTrack.query.filter_by(users_id=user.id,
                                                       sublist=sublist).first()

            if quiz_type == 'fill':
                current_progress = tracker.fill_progress
            if quiz_type == 'form':
                current_progress = tracker.form_progress
            if quiz_type == 'match':
                current_progress = tracker.match_progress
            if quiz_type == 'qna':
                current_progress = tracker.qna_progress
            if quiz_type == 'quiz':
                current_progress = tracker.quiz_progress

            if current_progress:
                print(f'\nThere is progress for {quiz_type} for sublist No. {sublist}!\n')  # DEBUG

                # takes the value of 'fill_progress' from databse and
                # gives it to 'correct_list'
                print('\nTaking the list from the database...\n')  # DEBUG
                correct_list = json.loads(current_progress)
                print(f'\ncorrect_list was {correct_list}.\n')  # DEBUG

                if correct_id not in correct_list and quiz_type != 'quiz':
                    # append 'correct_id' to 'correct_list'
                    print('\nAppending the correct id to the list...\n')  # DEBUG
                    correct_list.append(correct_id)
                    print(f'\ncorrect_list is now {correct_list}.\n')  # DEBUG

                    # replaces the old content with the appended 'correct_list'
                    print('\nAdding to database...\n')  # DEBUG

                    if quiz_type == 'fill':
                        tracker.fill_progress = json.dumps(correct_list)
                    if quiz_type == 'form':
                        tracker.form_progress = json.dumps(correct_list)
                    if quiz_type == 'match':
                        tracker.match_progress = json.dumps(correct_list)
                    if quiz_type == 'qna':
                        tracker.qna_progress = json.dumps(correct_list)

                    db.session.commit()
                    print('\nDone!\n')  # DEBUG

                elif quiz_type == 'quiz':
                    before_length = len(correct_list)
                    for id in correct_id:
                        if id not in correct_list:
                            print('\nAppending the correct id to the list...\n')  # DEBUG
                            correct_list.append(id)
                            print(f'\ncorrect_list is now {correct_list}.\n')  # DEBUG
                        else:
                            print(f'\nWord {id} is not new progress...\n')  # DEBUG

                    if len(correct_list) != before_length:
                        # replaces the old content with the appended 'correct_list'
                        print('\nAdding to database...\n')  # DEBUG
                        tracker.quiz_progress = json.dumps(correct_list)
                        db.session.commit()
                        print('\nDone!\n')  # DEBUG

                else:
                    print(f'\nWord {correct_id} is not new progress...\n')  # DEBUG

            else:
                print(f'\nNo progress found for {quiz_type} for sublist No. {sublist}!\n')  # DEBUG

                # append 'correct_id' to 'correct_list'
                print('\nAppending the correct id to the list...\n')  # DEBUG
                if quiz_type != 'quiz':
                    correct_list.append(correct_id)
                else:
                    correct_list.extend(correct_id)
                    tracker.quiz_progress = json.dumps(correct_list)
                print(f'\ncorrect_list is now {correct_list}.\n')  # DEBUG

                # replaces the old content with the appended 'correct_list'
                print('\nAdding to database...\n')  # DEBUG

                if quiz_type == 'fill':
                    tracker.fill_progress = json.dumps(correct_list)
                if quiz_type == 'form':
                    tracker.form_progress = json.dumps(correct_list)
                if quiz_type == 'match':
                    tracker.match_progress = json.dumps(correct_list)
                if quiz_type == 'qna':
                    tracker.qna_progress = json.dumps(correct_list)

                db.session.commit()
                print('\nDone!\n')  # DEBUG

    return ('From Python: Got it!')


# Quizzes
@app.route('/fill_in_the_blank', methods=['GET'])
def fill_in_the_blank():
    sublist = request.args.get('sublist')
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


@app.template_filter('json_loads')
def filter_json_loads(str):
    if str:
        result = json.loads(str)
    else:
        result = str
    return result


@app.template_filter('type')
def filter_tyoe(obj):
    result = type(obj)
    return result


@app.template_filter('score_count')
def filter_score_count(list):
    score = 0
    for i in json.loads(list):
        if i != 0:
            score += 1
    return score


@app.template_filter('enabled_only')
def _enabled_only(seq):
    result = [x for x in seq if not x.is_disabled]
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


@app.context_processor
def comp():
    def _comp(seq, sublist):
        result = [x for x in seq if x.sublist == sublist]
        return result
    return dict(comp=_comp)


if __name__ == '__main__':
    app.run(debug=True)
