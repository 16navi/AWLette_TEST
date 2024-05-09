from app import app
from flask import render_template, abort
from flask_sqlalchemy import SQLAlchemy
import os


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "AWL.db")
db.init_app(app)


import app.models as models


@app.route('/')
def homepage():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/sublist')
def all_words():
    return render_template("sublist.html")


@app.route('/sublist/words')
def sublist():
    words = models.Words.query.filter_by(sublist = 1).all()
    return render_template("words.html", words = words)


@app.route('/sublist/words/<int:id>')
def word(id):
    word = models.Words.query.filter_by(id = id).one()
    return render_template("word.html", word = word)


@app.route('/fill_in_the_blank')
def fill_in_the_blank():
    return render_template("fill_in_the_blank.html")


@app.route('/form')
def form():
    return render_template("form.html")


@app.route('/match')
def match():
    return render_template("match.html")


@app.route('/question_answer')
def question_answer():
    return render_template("question_answer.html")


@app.route('/quiz')
def quiz():
    return render_template("quiz.html")


if __name__ == "__main__":
    app.run(debug=True)