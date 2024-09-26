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


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('How about logging in first?')
    return redirect(url_for('homepage'))


# the object 'flask_login.current_user' can now be 
# called as 'user' from this point onward.
user = flask_login.current_user


# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_template.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('404_template.html'), 404


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
@flask_login.login_required
def admin_powers():
    if user.is_admin:
        return render_template('admin.html')
    else:
        flash(f"You're not Admin, are you, {user}?")
        return redirect(url_for('homepage'))


@app.route('/admin_powers/disable_account')
@flask_login.login_required
def disable_account():
    if user.is_admin:
        users = models.Users.query.filter_by(is_admin=None).all()
        return render_template('admin_disable_acc.html', users=users)
    else:
        flash(f"You're not Admin, are you, {user}?")
        return redirect(url_for('homepage'))


# Account disabler AJAX route
@app.route('/account_disabler', methods=['POST'])
def account_disabler():
    dict_key, dict_value = None, None
    # dict called 'disableDict' coming from disable account route
    #  posted through AJAX is requested here
    posted_dict = request.get_json()
    for key, value in posted_dict['disableDict'].items():
        dict_key, dict_value = key, value

    account = models.Users.query.filter_by(id=int(dict_value)).first()

    # dict_key can either be 'enable' or 'disable' depending on
    # how it is set up from the script for disable account route
    if dict_key == 'disable':
        account.is_disabled = 1
        db.session.commit()
    else:
        account.is_disabled = None
        db.session.commit()

    return ('From Python: Got it!')


@app.route('/admin_powers/disable_classroom')
@flask_login.login_required
def disable_classroom():
    if user.is_admin:
        classrooms = models.Classrooms.query.all()
        return render_template('admin_disable_classroom.html', classrooms=classrooms)
    else:
        flash(f"You're not Admin, are you, {user}?")
        return redirect(url_for('homepage'))


# Classroom disabler AJAX route
@app.route('/classroom_disabler', methods=['POST'])
def classroom_disabler():
    dict_key, dict_value = None, None
    #  dict called 'disableDict' coming from disable classroom route
    # posted through AJAX gets requested here
    posted_dict = request.get_json()
    for key, value in posted_dict['disableDict'].items():
        dict_key, dict_value = key, value

    classroom = models.Classrooms.query.filter_by(id=int(dict_value)).first()

    # dict_key can either be 'enable' or 'disable' depending on
    # how it is set up from the script for disable account route
    if dict_key == 'disable':
        classroom.is_disabled = 1
        db.session.commit()
    else:
        classroom.is_disabled = None
        db.session.commit()

    return ('From Python: Got it!')


@app.route('/admin_powers/teacher_request')
@flask_login.login_required
def teacher_request():
    if user.is_admin:
        requesting_teachers = models.Users.query.filter_by(is_teacher=0).all()
        return render_template('teacher_request.html',
                               requesting_teachers=requesting_teachers)
    else:
        flash(f"You're not Admin, are you, {user}?")
        return redirect(url_for('homepage'))


# Teacher request AJAX route
@app.route('/grant_or_reject', methods=['POST'])
def grant_or_reject():
    action, id = None, None
    # dict called 'grantDict' coming from teacher request route
    # posted through AJAX gets requested here
    posted_dict = request.get_json()
    for key, value in posted_dict.items():
        action = key
        id = value

    # key values of the dict can either be 'grant' or 'reject'
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


@app.route('/create_classroom', methods=['GET', 'POST'])
@flask_login.login_required
def create_classroom():
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
                    # 'generate_code' is a function imported from 'functions.py'
                    # open that file for further info about this function
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


@app.route('/classroom/<classroom_id>')
@flask_login.login_required
def classroom_stream(classroom_id):
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    if classroom:
        quizzes = models.Quiz.query.filter_by(classroom_id=classroom_id).all()
        if classroom.is_disabled:
            flash(f'Classroom {classroom} is disabled.')
            return redirect(url_for('homepage'))
        elif user.is_teacher == 1:
            return render_template('classroom_stream.html', classroom=classroom, quizzes=quizzes)
        else:
            if user in classroom.student:
                # from 'quizzes', remove all the quiz that this user has already taken
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
    else:
        flash('Classroom does not exist.')
        return redirect(url_for('homepage'))


# Quiz Archive AJAX Route
@app.route('/quiz_archiver', methods=['POST'])
def quiz_archiver():
    dict_value, dict_key = None, None
    # dict called 'archiveDict' coming from classroom stream route
    # posted through AJAX gets requested here
    posted_dict = request.get_json()
    for key, value in posted_dict['archiveDict'].items():
        dict_value = int(value)
        dict_key = key

    quiz = models.Quiz.query.filter_by(id=dict_value).first()

    # dict key can either be 'archive' or 'unarchive'
    if dict_key == 'archive':
        quiz.is_archived = 1
        db.session.commit()
    else:
        quiz.is_archived = None
        db.session.commit()

    return ('From Python: Got it!')


@app.route('/classroom/<classroom_id>/create_quiz', methods=['GET', 'POST'])
@flask_login.login_required
def create_quiz(classroom_id):
    if user.is_teacher == 1:
        form = Create_Quiz()
        classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
        if classroom:
            if request.method == 'GET':
                sublist = request.args.get('sublist')
                if sublist:
                    words = models.Words.query.filter_by(sublist=sublist).all()
                    if words:
                        return render_template('create_quiz.html', form=form,
                                               sublist=sublist,
                                               words=words,
                                               classroom=classroom)
                    else:
                        # this will only take place if the user manually types a sublist
                        # value through the URL because there are no buttons made that represent
                        # non-existent sublists.
                        flash('Sublist does not exist.')
                        return redirect(url_for('classroom_stream', classroom_id=classroom_id))
                else:
                    return render_template('create_quiz.html',
                                           form=form,
                                           sublist=sublist,
                                           classroom=classroom)
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
        else:
            flash('Classroom does not exist.')
            return redirect(url_for('homepage'))
    else:
        flash(f"You're not a teacher, are you, {user}?")
        return redirect(url_for('homepage'))


@app.route('/classroom/<classroom_id>/custom_quiz/<quiz_id>')
@flask_login.login_required
def custom_quiz(classroom_id, quiz_id):
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    if classroom:
        if user not in classroom.student:
            flash(f'This quiz is not for you, {user}.')
            return redirect(url_for('classroom_stream', classroom_id=classroom_id))
        
        # 'quiz' will contain the quiz set-up, which is created by the teacher
        # using the 'create quiz' route. Note that this does not contain the exact questions
        # and answers as is, but rather a set of possible question types that the quiz will
        # contain, along with the word pool that the quiz may choose the words to ask from,
        # as well as the name of the quiz and the amount of questions that it will ask.
        quiz = models.Quiz.query.filter_by(id=quiz_id).first()

        # the query for 'quiz_progress' takes any entry from the assosciation table 'UserQuiz'
        # that meet the specified conditions, which ultimately represents whether or not a user
        # has taken a quiz
        quiz_progress = models.UserQuiz.query.filter_by(users_id=user.id, quiz_id=quiz_id).first()

        if not quiz_progress and quiz:
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
        elif quiz_progress:
            flash(f"You've already done this quiz, {user}")
            return redirect(url_for('classroom_stream', classroom_id=classroom_id))
        else:
            flash('Quiz does not exist.')
            return redirect(url_for('classroom_stream', classroom_id=classroom_id))
    else:
        flash('Classroom does not exist.')
        return redirect(url_for('homepage'))


@app.route('/classroom/<classroom_id>/custom_quiz_progress/<quiz_id>')
@flask_login.login_required
def custom_quiz_progress(classroom_id, quiz_id):
    if user.is_teacher == 1:
        classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
        if classroom:
            quiz = models.Quiz.query.filter_by(id=quiz_id).first()
            if quiz:
                trackers = models.UserQuiz.query.filter_by(quiz_id=quiz_id).all()
                not_answered = classroom.student
                if trackers:
                    for tracker in trackers:
                        not_answered.remove(tracker.student)

                    return render_template('custom_quiz_progress.html',
                                           trackers=trackers,
                                           not_answered=not_answered,
                                           classroom=classroom)
                else:
                    return render_template('custom_quiz_progress.html',
                                           trackers=trackers,
                                           not_answered=not_answered,
                                           classroom=classroom)
            else:
                flash('Quiz does not exist.')
                return redirect(url_for('classroom_stream', classroom_id=classroom_id))
        else:
            flash('Classroom does not exist.')
            return redirect(url_for('homepage'))
    else:
        flash(f"You're not a teacher, are you, {user}?")
        return redirect(url_for('homepage'))


# Custom Quiz AJAX
@app.route('/custom_quiz_tracker', methods=['POST'])
def custom_quiz_tracker():
    dict_values = []

    # dict called 'correctItem' from the custom quiz route
    # posted through AJAX gets requested here
    posted_dict = request.get_json()
    for key, value in posted_dict['correctItem'].items():
        dict_values.append(value)

    # the value of 'correctItem' is a list containing all the id of
    # the words that the user got right, hence the list comprehension
    quiz_id = dict_values[0]
    correct_list = [i for i in dict_values[1]]
    user_id = dict_values[2]

    # This happens if a user goes back to the quiz after submitting and manages
    # to trigger the submission of the form again, thus submitting an empty list of
    # correct id
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

    # 'score' is a column in the assosciation table 'UserQuiz'
    quiz_tracker.score = json.dumps(correct_list)
    db.session.commit()

    return ('From Python: Got it!')


@app.route('/classroom/<classroom_id>/people')
@flask_login.login_required
def people(classroom_id):
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    if classroom:
        teacher = models.Users.query.filter_by(id=classroom.teacher_id).first()
        return render_template('people.html',
                               classroom=classroom,
                               teacher=teacher)
    else:
        flash('Classroom does not exist.')
        return redirect(url_for('homepage'))


@app.route('/classroom/<classroom_id>/people/<users_id>')
@flask_login.login_required
def student_progress(classroom_id, users_id):
    classroom = models.Classrooms.query.filter_by(id=classroom_id).first()
    if classroom:
        if user.is_teacher == 1:
            student = models.Users.query.filter_by(id=users_id).first()
            if student:
                return render_template('student_progress.html', student=student, classroom=classroom)
            else:
                flash('Student does not exist.')
                return redirect(url_for('classroom_stream', classroom_id=classroom_id))
        else:
            flash(f"You're not a teacher, are you, {user}?")
            return redirect(url_for('homepage'))
    else:
        flash('Classroom does not exist.')
        return redirect(url_for('homepage'))


@app.route('/enrol', methods=['GET', 'POST'])
@flask_login.login_required
def enrol():
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
                # these appends adds the id of 'user' and the classroom id 
                # to the many-to-many relationship between the
                # table 'Users' and 'Classrooms'
                user.enrolment.append(classroom)
                classroom.student.append(user)
                db.session.commit()
                flash(f'Welcome to Classroom {classroom}, {user}!')
                return redirect(url_for('homepage'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not user.is_authenticated:
        form = Sign_Up()
        unique_user = None
        if request.method == 'GET':
            return render_template('signup.html',
                                   form=form)
        else:
            if form.validate_on_submit():
                new_user = models.Users()
                username = form.username.data
                password = encrypt(form.password.data)
                not_unique_user = new_user.query.filter_by(username=username).first()
                if not_unique_user:
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
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('homepage'))


@app.route('/user_details')
@flask_login.login_required
def user_details():
    return render_template('user_details.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/sublist')
def all_words():
    words = models.Words.query.all()
    return render_template('sublist.html', words=words)


@app.route('/sublist/<sublist>')
def sublist(sublist):
    form = Search_Bar()
    words = models.Words.query.filter_by(sublist=sublist).all()
    return render_template('words.html', words=words, form=form)


@app.route('/sublist/words/<word>')
def word_listed(word):
    form = Search_Bar()
    word = models.Words.query.filter_by(word=word).first()
    next_word = models.Words.query.filter_by(id=word.id + 1).first()
    previous_word = models.Words.query.filter_by(id=word.id - 1).first()
    return render_template('word_page.html',
                           form=form,
                           word=word,
                           next_word=next_word,
                           previous_word=previous_word)


@app.route('/sublist/words/lookfor', methods=['GET'])
def word_lookfor():
    form = Search_Bar()
    # making the search input into lowercase makes it compatible
    # with searching through the 'Words' table as all the words in 
    # it are in lowercase as well.
    lower_word = str.lower(request.args.get('searching'))
    word = models.Words.query.filter_by(word=lower_word).first()
    if word:
        # the variables 'next_word' and 'previous_word' are for the next and previous
        # feature in the words route to work. The template handles cases of extraneous 
        # values of id (word id less than 1, more than 60)
        next_word = models.Words.query.filter_by(id=word.id + 1).first()
        previous_word = models.Words.query.filter_by(id=word.id - 1).first()
        return render_template('word_page.html',
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
    sublist, quiz_type = None, None
    dict_values, dict_keys, correct_list, correct_id = [], [], [], []
    # dict called 'correctItem' from all the quiz routes
    # posted through AJAX gets requested here
    posted_dict = request.get_json()

    # the dict contains two key-value pairs
    for key, value in posted_dict['correctItem'].items():
        dict_keys.append(key)
        dict_values.append(value)

    sublist = int(dict_values[1])
    quiz_type = dict_keys[0]

    if quiz_type != 'quiz':
        # quiz types other than quiz has this value as single integer...
        correct_id = int(dict_values[0])
    else:
        # ...but quiz has this value as a list
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

            # the first commit only adds the user id and the sublist to the newly-created
            # tracker. Now that a tracker for this sublist and user exists, it will then be
            # queried with 'tracker' so the progress can be added

            tracker = models.ProgTrack.query.filter_by(users_id=user.id,
                                                       sublist=sublist).first()

            if quiz_type != 'quiz':
                # notice the difference between append (single integer 
                # for quiz types other than 'quiz')...
                correct_list.append(correct_id)
            else:
                # ...and extend (quiz type 'quiz' has a list for its 
                # correct id value)
                correct_list.extend(correct_id)
                tracker.quiz_progress = json.dumps(correct_list)

            # json.dumps converts the python integer, or list, back into
            # a JSON string
            if quiz_type == 'fill':
                tracker.fill_progress = json.dumps(correct_list)
            if quiz_type == 'form':
                tracker.form_progress = json.dumps(correct_list)
            if quiz_type == 'match':
                tracker.match_progress = json.dumps(correct_list)
            if quiz_type == 'qna':
                tracker.qna_progress = json.dumps(correct_list)

            db.session.commit()

        # if 'tracker' exists, hence, if there is recorded progress for
        # any quiz
        else:
            tracker = models.ProgTrack.query.filter_by(users_id=user.id,
                                                       sublist=sublist).first()

            if quiz_type == 'fill':
                current_progress = tracker.fill_progress
            elif quiz_type == 'form':
                current_progress = tracker.form_progress
            elif quiz_type == 'match':
                current_progress = tracker.match_progress
            elif quiz_type == 'qna':
                current_progress = tracker.qna_progress
            elif quiz_type == 'quiz':
                current_progress = tracker.quiz_progress

            if current_progress:
                print(f'\nThere is progress for {quiz_type} for sublist No. {sublist}!\n')  # DEBUG
                print('\nTaking the list from the database...\n')  # DEBUG
                # straight out of the query, 'current_progress' is a JSON string, so it
                # needs to be turned into a python list first.
                correct_list = json.loads(current_progress)
                print(f'\ncorrect_list was {correct_list}.\n')  # DEBUG

                if correct_id not in correct_list and quiz_type != 'quiz':
                    print('\nAppending the correct id to the list...\n')  # DEBUG
                    correct_list.append(correct_id)
                    print(f'\ncorrect_list is now {correct_list}.\n')  # DEBUG
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

                # 'quiz' quiz type needs a seperate processing of correct id because
                # it uses lists instead of single integers
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
                        print('\nAdding to database...\n')  # DEBUG
                        tracker.quiz_progress = json.dumps(correct_list)
                        db.session.commit()
                        print('\nDone!\n')  # DEBUG

                else:
                    print(f'\nWord {correct_id} is not new progress...\n')  # DEBUG

            else:
                print(f'\nNo progress found for {quiz_type} for sublist No. {sublist}!\n')  # DEBUG

                print('\nAppending the correct id to the list...\n')  # DEBUG
                if quiz_type != 'quiz':
                    correct_list.append(correct_id)
                else:
                    correct_list.extend(correct_id)
                    tracker.quiz_progress = json.dumps(correct_list)
                print(f'\ncorrect_list is now {correct_list}.\n')  # DEBUG

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
    # the form for this request comes from the sublist picker that
    # shows up after opening every quiz once. This is present in all other
    # quiz types as well.
    sublist = request.args.get('sublist')
    words = models.Words.query.filter_by(sublist=sublist).all()
    random_forms = []
    if words:
        all_forms = []
        for word in words:
            add = [word.form[0],
                   word.form[1],
                   word.form[2]]
            all_forms.extend(add)

        # I am not worried about two or more forms coming
        # from the same word because, ultimately, these forms
        # are unique words as well.
        random_forms = random.sample(all_forms, 5)
    else:
        sublist = None

    return render_template('fill_in_the_blank.html',
                           sublist=sublist,
                           random_forms=random_forms)


@app.route('/form', methods=['GET'])
def form():
    sublist = request.args.get('sublist')
    words = models.Words.query.filter_by(sublist=sublist).all()

    # 'random_forms_main' is a nested list that will contain
    # 'random_forms_sublist'.
    random_forms_main = []
    random_blank_main = []
    random_blank_amount = 0

    if words:
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

        # Count how many blank items will be generated. This is needed
        # for automating the reload after getting all the answers right
        for content in random_blank_main:
            for i in content:
                random_blank_amount += i

        # This list will be nested inside 'random_forms_main' so that
        # for each item, which means for each three-item row in the quiz,
        # there is a corresponding three-item list of 0's and 1's that
        # decide whether an input field is blank or not.
        random_forms_sublist = []

        for word in random_words:

            add = [word.form[0],
                   word.form[1],
                   word.form[2]]
            random_forms_sublist.extend(add)
            random_forms_main.append(random_forms_sublist)

            # the same logic applies for containing the forms in that
            # for each three-item row, there is a corresponding three-item
            # list of words all nested in a '..._main' list.
            random_forms_sublist = []
    else:
        sublist = None

    return render_template('form.html',
                           sublist=sublist,
                           random_forms_main=random_forms_main,
                           random_blank_main=random_blank_main,
                           random_blank_amount=random_blank_amount)


@app.route('/match', methods=['GET'])
def match():
    sublist = request.args.get('sublist')
    words = models.Words.query.filter_by(sublist=sublist).all()
    random_words = []

    # This array of 1's and 0's will decide whether a button
    # is a 'word' button or 'definition' button, shuffled for
    # randomness
    arrange = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    random.shuffle(arrange)

    if words:
        random_words = random.sample(words, 5)
    else:
        sublist = None

    return render_template('match.html',
                           sublist=sublist,
                           random_words=random_words,
                           arrange=arrange)


@app.route('/question_answer', methods=['GET'])
def question_answer():
    sublist = request.args.get('sublist')
    words = models.Words.query.filter_by(sublist=sublist).all()
    # these variables are initialised so the template can still
    # be rendered while passing these variables even while there
    # is no value for sublist yet
    random_words = None
    question_type = None
    question_form_class = None

    if words:
        random_words = random.sample(words, 4)

        # the numbers 1-5 means different types of questions 
        # (see template for 'question_answer')
        question_type = random.randint(1, 5)

        if question_type == 4:
            # the numbers 1-3 for this variable represents either
            # a noun, verb, or adjective
            question_form_class = random.randint(1, 3)
    else:
        sublist = None

    return render_template('question_answer.html',
                           sublist=sublist,
                           random_words=random_words,
                           question_type=question_type,
                           question_form_class=question_form_class)


@app.route('/quiz', methods=['GET'])
def quiz():
    sublist = request.args.get('sublist')
    words = models.Words.query.filter_by(sublist=sublist).all()
    question_amount = 5

    if not words:
        sublist = None

    # The randomisation of the question types along with the
    # choices is handled inside the template using jinja
    # with the use of various filters and context processor
    # functions as well.

    return render_template('quiz.html',
                           sublist=sublist,
                           words=words,
                           question_amount=question_amount)


# Custom Jinja filters
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
def filter_enabled_only(seq):
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
