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


@app.route('/all_words')
def all_words():
    return render_template("all_words.html")


@app.route('/all_words/word')
def word():
    return render_template("word.html")


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