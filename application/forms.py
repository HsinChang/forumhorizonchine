"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms.ext.appengine.ndb import model_form

from .models import ExhibitorModel

def username_exist_check(form, field):
    """check if the username registered is already userd"""
    username = field.data
    member = ExhibitorModel.query(ExhibitorModel.username==username).get()
    if member:
        raise validators.ValidationError('username exists, choose a different one!')

class LoginForm(wtf.Form):
    """form userd for login"""
    username = wtf.TextField('Username', validators=[validators.InputRequired()])
    password = wtf.PasswordField('Password', validators=[validators.InputRequired()])

class RegisterForm(wtf.Form):
    """form user for registering and creating new member"""
    username = wtf.TextField('Username', validators=[validators.InputRequired(), username_exist_check])
    password = wtf.PasswordField('Password', validators=[validators.InputRequired()])
    password_confirm = wtf.PasswordField('Confirm password', validators=[validators.EqualTo('password')])
#    role = wtf.SelectField('Role', validators=[validators.InputRequired()], choices=[('ADMIN', 'ADMIN'), ('MEMBER', 'MEMBER')])
#    first_name = wtf.TextField('First name', validators=[validators.InputRequired()])
#    last_name = wtf.TextField('Last name', validators=[validators.InputRequired()])
    email = wtf.TextField('Email', validators=[validators.Email()])
    entreprise = wtf.TextField('Entreprise', validators=[validators.InputRequired()])

class JobForm(wtf.Form):
    title = wtf.TextField('Title', validators=[validators.InputRequired()])
    type = wtf.SelectField('Type', choices=[('job', 'job'), ('internship', 'internship')])
    content = wtf.TextAreaField('Content', validators=[validators.InputRequired()])
