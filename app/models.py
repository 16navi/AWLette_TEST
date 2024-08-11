from app.routes import db
from flask_login import UserMixin

# reset auto-increment: UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = 'ProgTrack';

WordSynonym = db.Table('WordSynonym',
                       db.Column('word_id', db.Integer, db.ForeignKey('Words.id')),
                       db.Column('synonym_id', db.Integer, db.ForeignKey('Synonyms.id'))
                       )


WordCollocation = db.Table('WordCollocation',
                           db.Column('word_id', db.Integer, db.ForeignKey('Words.id')),
                           db.Column('collocation_id', db.Integer, db.ForeignKey('Collocations.id'))
                           )


class Words(db.Model):
    __tablename__ = 'Words'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    sublist = db.Column(db.Integer())
    word = db.Column(db.Text())
    picture = db.Column(db.Text())
    # One-to-Many Relationships
    definition = db.relationship('Definitions', backref='definition_word')
    form = db.relationship('Forms', backref='form_word')
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
                                   back_populates='synonym'
                                   )

    def __repr__(self):
        return self.synonym


class Collocations(db.Model):
    __tablename__ = 'Collocations'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    collocation = db.Column(db.Text())
    # Many-to-Many Relationship
    collocation_word = db.relationship('Words',
                                       secondary='WordCollocation',
                                       back_populates='collocation'
                                       )

    def __repr__(self):
        return self.collocation


class Users(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.Text())
    password = db.Column(db.Text())
    progtrack = db.relationship('ProgTrack', backref='progtrack_users')
    # __table_args__ = (
    #     db.UniqueConstraint('username', 'password'),
    # )

    def __repr__(self):
        return self.username


class ProgTrack(db.Model):
    __tablename__ = 'ProgTrack'
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    fill_progress = db.Column(db.Text())
    form_progress = db.Column(db.Text())
    match_progress = db.Column(db.Text())
    qna_progress = db.Column(db.Text())
    quiz_progress = db.Column(db.Text())