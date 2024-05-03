from app.routes import db

class AWL(db.Model):
    __tablename__ = "Words"
    word_id = db.Column(db.Integer, primary_key = True, nullable = False)
    sublist = db.Column(db.Integer())
    word = db.Column(db.Text())
    picture = db.Column(db.Text())
