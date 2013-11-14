"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from application import app
from flaskext import wtf
from flask_login import current_user
from flask_babel import lazy_gettext
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


def job_lang_check(lang):
    """
    closure to check specific lang property

    Arguments:
    - `lang`:
    """
    lang = lang
    def job_check(form, field):
        """
        this is to check if job properties are well edited:
        job title and content should not be empty if it is published

        Arguments:
        - `from`:
        - `field`:
        """
        data = field.data
        published = getattr(form, 'publish_'+lang)
        if published.data:
            if len(data) == 0:
                raise validators.ValidationError('field should not be empty if you choose to publish it')
    return job_check

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

_lang_choices = zip(sorted(app.config['LOCALES']), sorted(app.config['LANGUAGES'].keys()))
class JobForm(wtf.Form):
    type = SelectField('Type', choices=[('Job', _('Job')), ('Internship', _('Internship'))])
    is_online = BooleanField('apply online')
    apply_url = StringField('apply URL')
    enterprise = SelectField('Enterprise')
    enterprise_mail = SelectField('Enterprise_Mail')
    publish_en = BooleanField('Publish', default=True)
    publish_zh = BooleanField('Publish', default=True)
    publish_fr = BooleanField('Publish', default=True)
    title_en = StringField('Title', validators=[job_lang_check('en')])
    title_zh = StringField('Title', validators=[job_lang_check('zh')])
    title_fr = StringField('Title', validators=[job_lang_check('fr')])
    content_en = TextAreaField('Content', validators=[job_lang_check('en')])
    content_zh = TextAreaField('Content', validators=[job_lang_check('zh')])
    content_fr = TextAreaField('Content', validators=[job_lang_check('fr')])

    default_lang = SelectField('Default version', choices=_lang_choices)
    cv_required = SelectMultipleField('required CV and letter of motivation("use the Key Ctrl to select multi")', choices=_lang_choices, validators=[validators.InputRequired()])


class EnterpriseForm(wtf.Form):
    name = StringField('Name', validators=[validators.InputRequired(), enterprise_exist_check])
    shortname = StringField('Short name', validators=[validators.InputRequired()])
    #at lest one email
    email = StringField('Email', validators=[validators.Email()])

class EmailForm(wtf.Form):
    email = StringField('Email', validators=[validators.Email()])

class ContactForm(wtf.Form):
    first_name = StringField(lazy_gettext(u'First name'), validators=[validators.InputRequired()])
    last_name = StringField(lazy_gettext(u'Last name'), validators=[validators.InputRequired()])
    email = StringField(lazy_gettext(u'Email'), validators=[validators.Email()])
    message = TextAreaField(lazy_gettext(u'Message'), validators=[validators.InputRequired()])
