"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms.ext.appengine.ndb import model_form

from .models import UserModel, EnterpriseModel

def username_exist_check(form, field):
    """check if the username registered is already userd"""
    username = field.data
    user = UserModel.query(UserModel.username==username).get()
    if user:
        raise validators.ValidationError('username exists, choose a different one!')

def enterprise_exist_check(form, field):
    name = field.data
    enterprise = EnterpriseModel.query(EnterpriseModel.name==name).get()
    if enterprise:
        raise validators.ValidationError('enterprise exists, you don\'t need to create it again!')

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
    company = wtf.TextField('Company', validators=[validators.InputRequired()])


class JobForm(wtf.Form):
    title = wtf.TextField('Title', validators=[validators.InputRequired()])
    type = wtf.SelectField('Type', choices=[('job', 'job'), ('internship', 'internship')])
    enterprise_mail = wtf.SelectField('Enterprise_Mail',)
    content = wtf.TextAreaField('Content', validators=[validators.InputRequired()])


class EnterpriseForm(wtf.Form):
    name = wtf.TextField('Name', validators=[validators.InputRequired(), enterprise_exist_check])
    shortname = wtf.TextField('Short name', validators=[validators.InputRequired()])
    #at lest one email
    email = wtf.TextField('Email', validators=[validators.Email()])

class EmailForm(wtf.Form):
    email = wtf.TextField('Email', validators=[validators.Email()])
