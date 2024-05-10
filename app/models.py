from app.routes import db


WordSynonym = db.Table('WordSynonym',
                       db.Column('word_id', db.Integer, db.ForeignKey('Word.id')),
                       db.Column('synonym_id', db.Integer, db.ForeignKey('Synonym.id')))


class Words(db.Model):
    __tablename__ = 'Words'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    sublist = db.Column(db.Integer())
    word = db.Column(db.Text())
    picture = db.Column(db.Text())
    #One-to-Many Relationships
    definition = db.relationship('Definitions', backref = 'definition_word')
    form = db.relationship('Forms', backref = 'form_word')

    def __repr__(self):
        return self.word


class Definitions(db.Model):
    __tablename__ = 'Definitions'
    word_id = db.Column(db.Integer, db.ForeignKey('Words.id'))
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    definition = db.Column(db.Text())
    type = db.Column(db.Integer())

    def __repr__(self):
        return self.definition
    

class Forms(db.Model):
    __tablename__ = 'Forms'
    word_id = db.Column(db.Integer, db.ForeignKey('Words.id'))
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    form = db.Column(db.Text())
    form_class = db.Column(db.Integer())
    sentence = db.Column(db.Text())


    def __repr__(self):
        return self.form
    

class Synonym(db.Model):
    __tablename__ = 'Synonym'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    synonym = db.Column(db.Text())