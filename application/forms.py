"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, FormField, SelectMultipleField
from wtforms import validators
from passlib.apps import custom_app_context as pwd_context
from .models import UserModel, EnterpriseModel

def username_exist_check(form, field):
    """check if the username registered is already userd"""
    username = field.data
    user = UserModel.query(UserModel.username==username).get()
    if user:
        raise validators.ValidationError('username exists, choose a different one!')

def old_password_check(form, field):
    """check old password input is valide"""
    old_password = field.data
    password = current_user.password
    r = pwd_context.verify(old_password, current_user.password)
    if not r:
        raise validators.ValidationError('old password is wrong')

def enterprise_exist_check(form, field):
    name = field.data
    enterprise = EnterpriseModel.query(EnterpriseModel.name==name).get()
    if enterprise:
        raise validators.ValidationError('enterprise exists, you don\'t need to create it again!')

class LoginForm(wtf.Form):
    """form userd for login"""
    username = StringField('Username', validators=[validators.InputRequired()])
    password = PasswordField('Password', validators=[validators.InputRequired()])

class RegisterForm(wtf.Form):
    """form user for registering and creating new member"""
    username = StringField('Username', validators=[validators.InputRequired(), username_exist_check])
    password = PasswordField('Password', validators=[validators.InputRequired()])
    password_confirm = PasswordField('Confirm password', validators=[validators.EqualTo('password')])
#    role = wtf.SelectField('Role', validators=[validators.InputRequired()], choices=[('ADMIN', 'ADMIN'), ('MEMBER', 'MEMBER')])
#    first_name = wtf.TextField('First name', validators=[validators.InputRequired()])
#    last_name = wtf.TextField('Last name', validators=[validators.InputRequired()])
    email = StringField('Email', validators=[validators.Email()])
    company = StringField('Company', validators=[validators.InputRequired()])


class PasswordForm(wtf.Form):
    old_password = PasswordField('Old password', validators=[validators.InputRequired(), old_password_check])
    new_password = PasswordField('New password', validators=[validators.InputRequired()])
    confirm_password = PasswordField('Confirm password', validators=[validators.EqualTo('new_password')])


class JobMetaForm(wtf.Form):
    publish = BooleanField('publish')
    title = StringField('Title')
    content = TextAreaField('Content')
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(JobMetaForm, self).__init__(*args, **kwargs)


class JobForm(wtf.Form):
    type = SelectField('Type', choices=[('job', 'job'), ('internship', 'internship')])
    enterprise_mail = SelectField('Enterprise_Mail')
    # en = FormField(JobMetaForm, 'en')
    # fr = FormField(JobMetaForm, 'fr')
    # zh = FormField(JobMetaForm, 'zh')
    publish_en = BooleanField('Publish', default=True)
    publish_zh = BooleanField('Publish', default=True)
    publish_fr = BooleanField('Publish', default=True)
    title_en = StringField('Title')
    title_zh = StringField('Title')
    title_fr = StringField('Title')
    content_en = TextAreaField('Content')
    content_zh = TextAreaField('Content')
    content_fr = TextAreaField('Content')

    default_lang = SelectField('Default version', choices=[('en', 'en'), ('fr', 'fr'), ('zh', 'zh')])
    cv_required = SelectMultipleField('required CV and letter of motivation("use the Key Ctrl to select multi")', choices=[('en', 'en'), ('fr', 'fr'), ('zh', 'zh')], validators=[validators.InputRequired()])


class EnterpriseForm(wtf.Form):
    name = StringField('Name', validators=[validators.InputRequired(), enterprise_exist_check])
    shortname = StringField('Short name', validators=[validators.InputRequired()])
    #at lest one email
    email = StringField('Email', validators=[validators.Email()])

class EmailForm(wtf.Form):
    email = StringField('Email', validators=[validators.Email()])
