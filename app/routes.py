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