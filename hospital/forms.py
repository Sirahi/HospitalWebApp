from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email

from hospital.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    specialization = StringField('Specialization')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    checked = BooleanField('Check this box if you are a doctor', id='checked')
    doc = SelectField('Doctors', id='doc')
    submit = SubmitField('Register')

    def validate_username(self, username):
        doctor = User.query.filter_by(username=username.data).first()
        if doctor is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        doctor = User.query.filter_by(email=email.data).first()
        if doctor is not None:
            raise ValidationError('Please use a different email address.')


class ChangeDoctorForm(FlaskForm):
    doc = SelectField('Doctors', id='doc')
    submit = SubmitField('Change')


class AddDiagnosisForm(FlaskForm):
    name = StringField('Specify Diagnosis', validators=[DataRequired()])
    explanation = StringField('Explanation', validators=[DataRequired()])
    submit = SubmitField('Add Diagnosis')
