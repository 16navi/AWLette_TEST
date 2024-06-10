from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, ValidationError
import app.models as models

# Add a class for the different forms that
# we will use---as done on Mr. D's example.

class Sign_Up(FlaskForm):

    def uniqueUser(form, field, user_list):
        for i in user_list:
            if field.data == i:
                raise ValidationError('Already taken!')

    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])