from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional


# Add a class for the different forms that
# we will use---as done on Mr. D's example.


class Search_Bar(FlaskForm):
    searching = StringField('username', validators=[InputRequired()])


class Sign_Up(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    is_teacher = BooleanField('is_teacher')


class Log_In(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])


class Create_Classroom(FlaskForm):
    classroom_name = StringField('classroom_name', validators=[InputRequired()])
    description = TextAreaField('description', validators=[Optional(), Length(min=10, max=100)])


class Enrol(FlaskForm):
    code = StringField('code', validators=[InputRequired()])