from app.routes import db

class Words(db.Model):
    __tablename__ = "Words"
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    sublist = db.Column(db.Integer())
    word = db.Column(db.Text())
    picture = db.Column(db.Text())
    definition = db.relationship("Definitions", backref = "words")

    def __repr__(self):
        return self.name
    
class Definitions(db.Model):
    __tablename__ = "Definitions"
    word_id = db.Column(db.Integer, db.ForeignKey("Words.id"))
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    definition = db.Column(db.Text())
    type = db.Column(db.Integer())

    def __repr__(self):
        return self.definition