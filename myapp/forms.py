
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField ,PasswordField, validators
from wtforms.validators import InputRequired, DataRequired, Optional, URL, Length, NumberRange, EqualTo, Email

class AddUsers(FlaskForm):
    """Form for creating Users"""
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField('Email Address', [Email(message='Invalid email'), Length(min=6, max=50)])
    username = StringField("Username", validators=[InputRequired()])  
    create_password = PasswordField("Password", [validators.DataRequired(),
                                                validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('create_password', message='Passwords must match')])

class Login(FlaskForm):
    "form for logging in"
    username = StringField("Username", validators=[InputRequired(message="Wrong Username")])  
    password = PasswordField("Password", [validators.DataRequired()])


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

