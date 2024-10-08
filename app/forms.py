from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, SelectMultipleField, widgets, HiddenField
from wtforms.validators import InputRequired, Length, Optional, NumberRange, ValidationError

# this is used by the form 'Create_Quiz'
types = [
    (1, 'given the definition, answer with the word.'),
    (2, 'given the word, answer with the definition.'),
    (3, 'given the word, answer with its synonym.'),
    (4, 'given the word, answer with what figure of speech it is (noun, adjective, verb).'),
    (5, 'given the word, answer with its collocation.'),
]


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


# Should probably take off validator here since checkboxes are 
# being validated already with js, as well as word pool
class Create_Quiz(FlaskForm):
    def choose_one(form, field):
        if len(field.data) == 0:
            print('hi!') #  DEBUG
            raise ValidationError('Choose at least one.')

    name = StringField('name', validators=[InputRequired()])
    item = IntegerField('item', validators=[InputRequired(), NumberRange(min=5, max=60)])
    question_type = MultiCheckboxField('question_type', choices=types, validators=[choose_one], coerce=int)
    word_pool = HiddenField('word_pool')