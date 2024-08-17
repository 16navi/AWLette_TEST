from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, SelectMultipleField, widgets, HiddenField
from wtforms.validators import InputRequired, Length, Optional, NumberRange, ValidationError


# Add a class for the different forms that
# we will use---as done on Mr. D's example.

types = [
    (1, '1 - given the definition, answer with the word.'),
    (2, '2 - given the word, answer with the definition.'),
    (3, '3 - given the word, answer with its synonym.'),
    (4, '4 - given the word, answer with what figure of speech it is (noun, adjective, verb).'),
    (5, '5 - given the word, answer with its collocation.'),
]


# class ChooseOne():
#     def __init__(self, message=None):
#         if not message:
#             message = 'Choose at least one.'
#         self.message = message
    
#     def __call__(self, form, field):
#         if not form.data:
#             print('hi!') #  DEBUG
#             raise ValidationError(self.message)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(html_tag='ol', prefix_label=False)
    option_widget = widgets.CheckboxInput()


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


# Should probably take off validator here since checkboxes are being handled by js
class Create_Quiz(FlaskForm):
    def choose_one(form, field):
        if len(field.data) == 0:
            print('hi!') #  DEBUG
            raise ValidationError('Choose at least one.')

    item = IntegerField('item', validators=[InputRequired(), NumberRange(min=5, max=60)])
    question_type = MultiCheckboxField('question_type', choices=types, validators=[choose_one])
    word_pool = HiddenField('word_pool')