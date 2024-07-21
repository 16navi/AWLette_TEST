from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired


# Add a class for the different forms that
# we will use---as done on Mr. D's example.


class Search_Bar(FlaskForm):
    searching = StringField('username', validators=[InputRequired()])


class Sign_Up(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])


class Log_In(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
