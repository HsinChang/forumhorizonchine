# from flask_admin import Admin, BaseView, expose

# class AdminView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/index.html')
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.ext import ndb
from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
from forms import RegisterForm, JobForm, EnterpriseForm, EmailForm, PasswordForm
from models import UserModel, JobModel, JobMetaModel, ROLES, EnterpriseModel, EmailModel
from decorators import admin_required
from application import app
from passlib.apps import custom_app_context as pwd_context
import flask_login
from os.path import splitext
import json

admin = Blueprint('admin', __name__)

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = UserModel.query(UserModel.username==username).get()
        if user and pwd_context.verify(password, user.password) and user.role == ROLES['ADMIN']:
            result = flask_login.login_user(user)
            flash('login succeeded!')
        else:
            flash('login failed')
    return redirect(url_for('admin.index'))

@admin.route('/logout', methods=['GET', 'POST'])
@admin_required
def logout():
    """
    logout admin
    """
    flask_login.logout_user()
    return redirect(url_for('admin.index'))


@admin.route('/change_password', methods=['GET', 'POST'])
@admin_required
def change_password():
    form = PasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = flask_login.current_user
        user.password = pwd_context.encrypt(form.new_password.data)
        try:
            user.put()
            flash('password changed!')
            redirect(url_for('admin.index'))
        except CapabilityDisabledError:
            flash('error whan changing password')
    return render_template('admin/change_password.html', form=form)
@admin.route('/users')
@admin_required
def users():
    """
    user management
    """
    users = UserModel.query()
    return render_template('admin/users.html', users=users)

@admin.route('/edit_user/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_user(keyurl):
    """

    Arguments:
    - `keyurl`:
    """
    flash('TODO')
    return redirect(url_for('admin.users'))

@admin.route('/delete_user/<keyurl>', methods=['GET', 'POST'])
@admin_required
def delete_user(keyurl):
    """

    Arguments:
    - `keyurl`:
    """
    key = ndb.Key(urlsafe=keyurl)
    user = key.get()
    if user and user.role != 'admin':
        user.delete()
    else:
        flash('delete failed')
    redirect(url_for('amdin.users'))


@admin.route('/enterprises')
@admin_required
def enterprises():
    """
    """
    enterprises = EnterpriseModel.query()
    return render_template('admin/enterprises.html', enterprises=enterprises)

@admin.route('/new_enterprise', methods=['GET', 'POST'])
@admin_required
def new_enterprise():
    """
    """
    form = EnterpriseForm(request.form)
    if request.method == 'POST' and form.validate():
        e = EnterpriseModel(
            name = form.name.data,
            shortname = form.shortname.data,
        )
        try:
            e.put()
            email = EmailModel(
                enterprise = e.key,
                email = form.email.data
            )
            email.put()
            return redirect(url_for('admin.edit_enterprise', keyurl=e.key.urlsafe()))
        except CapabilityDisabledError:
            flash('error')
    return render_template('admin/new_enterprise.html', form=form)


@admin.route('/edit_enterprise/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_enterprise(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    e = key.get()
    if not e:
        flash(_('no such enterprise'))
        return redirect(url_for('admin.enterprises'))
    emails = EmailModel.query(EmailModel.enterprise==e.key)
    form = EnterpriseForm(request.form, obj=e)
    if request.method == 'POST' and form.validate():
            e.name = form.name.data
            e.shortname = form.shortname.data
            e.email = form.email.data
            try:
                e.put()
                return redirect(url_for('admin.enterprises'))
            except CapabilityDisabledError:
                flash('error')
    return render_template('admin/edit_enterprise.html', form=form, keyurl=keyurl, emails=emails)


@admin.route('/delete_enterprise/<keyurl>')
@admin_required
def delete_enterprise(keyurl):
    """

    Arguments:
    - `e_id`:
    """
    key = ndb.Key(urlsafe=keyurl)
    e = key.get()
    if not e:
        flash(_('no such enterprise'))
        return redirect(url_for('admin.enterprises'))
    emails = EmailModel.query(EmailModel.enterprise==key)
    keys = [e.key for e in emails]

    try:
        ndb.delete_multi(keys)
        e.key.delete()
    except CapabilityDisabledError:
        flash(_('fail to delete'))
    return redirect(url_for('admin.enterprises'))


@admin.route('/new_email/<keyurl>', methods=['GET', 'POST'])
@admin_required
def new_email(keyurl):
    """
    """
    key = ndb.Key(urlsafe=keyurl)
    form = EmailForm(request.form)
    if request.method == 'POST' and form.validate():
        email = EmailModel(
            enterprise = key,
            email = form.email.data
        )
        try:
            email.put()
            return redirect(url_for('admin.edit_enterprise', keyurl=keyurl))
        except CapabilityDisabledError:
            flash('save error')
    return render_template('admin/new_email.html', form=form, keyurl=keyurl)


@admin.route('/edit_email/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_email(keyurl):
    email = ndb.Key(urlsafe=keyurl).get()
    if not email:
        flash('no such email')
        return redirect(url_for('admin.enterprises'))
    form = EmailForm(request.form)
    if request.method == 'GET':
        form.email.data = email.email

    if request.method == 'POST' and form.validate():
        email.email = form.email.data
        try:
            email.put()
            return redirect(url_for('admin.edit_enterprise', keyurl=email.enterprise))
        except CapabilityDisabledError:
            flash('save error')
    return render_template('admin/edit_email.html', form=form, keyurl=keyurl)


@admin.route('/delete_email/<keyurl>', methods=['POST'])
@admin_required
def delete_email(keyurl):
    """

    Arguments:
    - `keyurl`:
    """
    email = ndb.Key(urlsafe=keyurl)
    if not email:
        flash('no such email')
        return redirect(url_for('admin.enterprises'))
    enterprise = email.enterprise
    email.key.delete()
    return redirect(url_for('admin/edit_enterprise', keyurl=enterpris))


@admin.route('/jobs')
@admin_required
def jobs():
    """
    all jobs
    """
    jobs = JobModel.query()
    return render_template('admin/jobs.html', jobs=jobs)

@admin.route('/new_job', methods=['GET', 'POST'])
@admin_required
def new_job():
    """
    create new job infos
    """
    form = JobForm(request.form)
    enterprises = EnterpriseModel.query()
    mails = EmailModel.query()

    form.enterprise.choices = [(e.key.urlsafe(), e.name) for e in enterprises]
    if len(form.enterprise.choices) == 0:
        #no enterprise, create one at first
        flash('there is no enterprise, please create one before add new job')
        return redirect(url_for('admin.new_enterprise'))

    grouped_emails = {str(e.key.urlsafe()): {} for e in enterprises}
    for m in mails:
        key = m.enterprise.urlsafe()
        grouped_emails[key][str(m.key.urlsafe())] = m.email

    key = form.enterprise.choices[0][0]
    form.enterprise_email.choices = grouped_emails[key].items()

    if request.method == 'POST' and form.validate():
        user = flask_login.current_user
        mail = ndb.Key(urlsafe=form.enterprise_email.data)
        enterprise = ndb.Key(urlsafe=form.enterprise.data)

        fr = {
            'published': form.publish_fr.data,
            'title': form.title_fr.data,
            'content': form.content_fr.data
        }
        en = {
            'published': form.publish_en.data,
            'title': form.title_en.data,
            'content': form.content_en.data
        }
        zh = {
            'published': form.publish_zh.data,
            'title': form.title_zh.data,
            'content': form.content_zh.data
        }
        meta = {
            "en": en,
            "fr": fr,
            "zh": zh
        }
        job = JobModel(
            type = form.type.data,
            is_online = form.is_online.data,
            enterprise = enterprise,
            enterprise_email = mail,
            meta = meta,
            published = fr["published"] or en["published"] or zh["published"],
            default_lang = form.default_lang.data,
            cv_required = form.cv_required.data,
       #     poster = user.key
        )
        try:
            job.put()
            return redirect(url_for('admin.jobs'))
        except CapabilityDisabledError:
            flash('add job error!')
    return render_template('admin/new_job.html', form=form, grouped_emails = json.dumps(grouped_emails))


@admin.route('/edit_job/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_job(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    job = key.get()
    if not job:
        flash(_('no such job'))
        return redirect(url_for('admin.jobs'))
    form = JobForm(request.form, obj=job)
    enterprises = EnterpriseModel.query()
    mails = EmailModel.query()

    form.enterprise.choices = [(e.key.urlsafe(), e.name) for e in enterprises]
    grouped_emails = {str(e.key.urlsafe()): {} for e in enterprises}
    for m in mails:
        key = m.enterprise.urlsafe()
        grouped_emails[key][str(m.key.urlsafe())] = m.email

    key = form.enterprise.choices[0][0]
    form.enterprise_email.choices = grouped_emails[key].items()

    if request.method == 'POST' and form.validate():
        job.type = form.type.data
        job.is_online = form.is_online.data
        mail = ndb.Key(urlsafe=form.enterprise_email.data)
        job.enterprise_email = mail
        job.enterprise = ndb.Key(urlsafe=form.enterprise.data)

        for lang in ['fr', 'en', 'zh']:
            job.meta[lang]['published'] = getattr(form, "publish_"+lang).data
            job.meta[lang]['title'] = getattr(form, "title_"+lang).data
            job.meta[lang]['content'] = getattr(form, "content_"+lang).data

        job.published = job.fr.published or job.en.published or job.zh.published
        job.default_lang = form.default_lang.data
        job.cv_required = form.cv_required.data
        try:
            job.put()
            return redirect(url_for('admin.jobs'))
        except CapabilityDisabledError:
            flash('error')
    elif request.method == 'GET':
    #GET handle goes here
        if job.enterprise:
            form.enterprise.data = job.enterprise.urlsafe()
            form.enterprise_email.choices = grouped_emails[form.enterprise.data].items()
        if job.is_online:
            form.is_online.data = True
            form.apply_url.data = job.apply_url
        else:
            form.enterprise_email.data = job.enterprise_email.urlsafe()

        for lang in ['fr', 'en', 'zh']:
            v = getattr(form, "publish_"+lang)
            v.data = job.meta[lang]['published']

            v = getattr(form, "title_"+lang)
            v.data = job.meta[lang]['title']

            v = getattr(form, "content_"+lang)
            v.data = job.meta[lang]['content']

    return render_template('admin/edit_job.html', form=form, keyurl=keyurl)


@admin.route('/delete_job/<keyurl>')
@admin_required
def delete_job(keyurl):
    """

    Arguments:
    - `keyurl`:
    """
    key = ndb.Key(urlsafe=keyurl)
    job = key.get()
    if not job:
        flash(_('no such job'))
        return redirect(url_for('admin.jobs'))
    try:
        job.key.delete()
    except CapabilityDisabledError:
        flash(_('fail to delete'))
    return redirect(url_for('admin.jobs'))

import data as Data
@admin.route('/data')
@admin_required
def data():
    """
    """
    return render_template('admin/data.html')

@admin.route('/data/import_enterprise', methods=['POST'])
@admin_required
def import_enterprise():
    """
    """
    f = request.files.values()[0]
    path, ext = splitext(f.filename)
    if ext != '.xml':
        #not xml file
        flash('not xml file')
    content = f.read()
    Data.import_enterprise(content)
    return redirect(url_for('admin.data'))

@admin.route('/data/export_enterprise')
def export_enterprise():
    """
    """
    output = Data.export_enterprise()
    return Response(output, mimetype='text/xml')

@admin.route('/data/import_jobs', methods=['POST'])
@admin_required
def import_jobs():
    """
    """
    f = request.files.values()[0]
    path, ext = splitext(f.filename)
    if ext != '.xml':
        #not xml file
        flash('not xml file')
    else:
        content = f.read()
        Data.import_jobs(content)
    return redirect(url_for('admin.data'))

@admin.route('/data/export_jobs')
@admin_required
def export_jobs():
    """
    """
    output = '<data></data>'
    return Reponse(output, mimetype='text/xml')

@admin.route('/')
def index():
    """
    """
    return render_template('base_admin.html')

def init_admin():
    role = ROLES['ADMIN']
    user = UserModel.query(UserModel.username=='admin').get()

    if user is None:
        #create admin
        password = pwd_context.encrypt('admin')
        admin = UserModel(
            username = 'admin',
            password = password,
            role = role,
            email = 'lutianming1005@gmail.com',
        )
        try:
            admin.put()
            print 'admin created'
        except CapabilityDisabledError:
            print 'creat fail'
    else:
        print 'admin exists'
