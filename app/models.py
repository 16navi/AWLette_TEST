from app.routes import db

class Words(db.Model):
    __tablename__ = "Words"
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    sublist = db.Column(db.Integer())
    word = db.Column(db.Text())
    picture = db.Column(db.Text())

    def __repr__(self):
        return self.name
