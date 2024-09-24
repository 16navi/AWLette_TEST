from app.routes import db
from flask_login import UserMixin

# reset auto-increment: UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = 'table_name';

WordSynonym = db.Table('WordSynonym',
                       db.Column('word_id', db.Integer, db.ForeignKey('Words.id')),
                       db.Column('synonym_id', db.Integer, db.ForeignKey('Synonyms.id')))


WordCollocation = db.Table('WordCollocation',
                           db.Column('word_id', db.Integer, db.ForeignKey('Words.id')),
                           db.Column('collocation_id', db.Integer, db.ForeignKey('Collocations.id')))


# Mutable association table
class UserQuiz(db.Model):
    __tablename__ = 'UserQuiz'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('Quiz.id'))
    score = db.Column(db.Integer())

    quiz = db.relationship('Quiz', backref='UserQuiz', viewonly=True)
    student = db.relationship('Users', backref='UserQuiz', viewonly=True)


# Mutable association table
class UserClassroom(db.Model):
    __tablename__ = 'UserClassroom'
    dummy_column = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    classrooms_id = db.Column(db.Integer, db.ForeignKey('Classrooms.id'))


class Words(db.Model):
    __tablename__ = 'Words'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    sublist = db.Column(db.Integer())
    word = db.Column(db.Text())
    picture = db.Column(db.Text())
    # One-to-Many Relationships
    definition = db.relationship('Definitions', backref='Words')
    form = db.relationship('Forms', backref='Words')
    # Many-to-Many Relationships
    synonym = db.relationship('Synonyms',
                              secondary='WordSynonym',
                              back_populates='synonym_word')
    collocation = db.relationship('Collocations',
                                  secondary='WordCollocation',
                                  back_populates='collocation_word')

    def __repr__(self):
        return self.word


class Definitions(db.Model):
    __tablename__ = 'Definitions'
    word_id = db.Column(db.Integer, db.ForeignKey('Words.id'))
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    definition = db.Column(db.Text())
    type = db.Column(db.Integer())

    def __repr__(self):
        return self.definition


class Forms(db.Model):
    __tablename__ = 'Forms'
    word_id = db.Column(db.Integer, db.ForeignKey('Words.id'))
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    form = db.Column(db.Text())
    form_class = db.Column(db.Integer())
    sentence = db.Column(db.Text())

    def __repr__(self):
        return self.form


class Synonyms(db.Model):
    __tablename__ = 'Synonyms'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    synonym = db.Column(db.Text())
    # Many-to-Many Relationship
    synonym_word = db.relationship('Words',
                                   secondary='WordSynonym',
                                   back_populates='synonym')

    def __repr__(self):
        return self.synonym


class Collocations(db.Model):
    __tablename__ = 'Collocations'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    collocation = db.Column(db.Text())
    # Many-to-Many Relationship
    collocation_word = db.relationship('Words',
                                       secondary='WordCollocation',
                                       back_populates='collocation')

    def __repr__(self):
        return self.collocation


class Users(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.Text())
    password = db.Column(db.Text())
    is_admin = db.Column(db.Integer())
    is_teacher = db.Column(db.Integer())
    is_disabled = db.Column(db.Integer())
    progtrack = db.relationship('ProgTrack', backref='Users')
    quiz_tracker = db.relationship('UserQuiz', backref='Users', viewonly=True)
    # Many-to-Many Relationship
    enrolment = db.relationship('Classrooms',
                                secondary='UserClassroom',
                                back_populates='student')
    finished_quiz = db.relationship('Quiz',
                                    secondary='UserQuiz',
                                    back_populates='student')

    def __repr__(self):
        return self.username


class ProgTrack(db.Model):
    __tablename__ = 'ProgTrack'
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    sublist = db.Column(db.Integer())
    fill_progress = db.Column(db.Text())
    form_progress = db.Column(db.Text())
    match_progress = db.Column(db.Text())
    qna_progress = db.Column(db.Text())
    quiz_progress = db.Column(db.Text())


class Classrooms(db.Model):
    __tablename__ = 'Classrooms'
    teacher_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    code = db.Column(db.Text())
    classroom = db.Column(db.Text())
    description = db.Column(db.Text())
    is_disabled = db.Column(db.Integer())
    quiz = db.relationship('Quiz', backref='Classrooms')

    # Many-to-Many Relationship
    student = db.relationship('Users',
                              secondary='UserClassroom',
                              back_populates='enrolment')

    def __repr__(self):
        return self.classroom


class Quiz(db.Model):
    __tablename__ = 'Quiz'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('Classrooms.id'))
    name = db.Column(db.Text())
    item = db.Column(db.Integer())
    word_pool = db.Column(db.Text())
    question_types = db.Column(db.Text())
    is_archived = db.Column(db.Integer())

    quiz_tracker = db.relationship('UserQuiz', backref='Quiz', viewonly=True)

    # Many-to-Many Relationship
    student = db.relationship('Users',
                              secondary='UserQuiz',
                              back_populates='finished_quiz')

    def __repr__(self):
        return self.name
