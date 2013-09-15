# from flask_admin import Admin, BaseView, expose

# class AdminView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/index.html')
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.ext import ndb
from flask import Blueprint, render_template, redirect, url_for, request, flash
from forms import RegisterForm, JobForm, EnterpriseForm, EmailForm
from models import UserModel, JobModel, ROLES, EnterpriseModel, EmailModel
from decorators import admin_required
from application import app

import flask_login

admin = Blueprint('admin', __name__)

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserModel.query(UserModel.username==username, UserModel.password==password).get()
        if user and user.role == ROLES['ADMIN']:
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
def edit_mail(keyurl):
    email = ndb.Key(keyurl).get()
    if not email:
        flash('no such email')
        return redirect(url_for('admin.enterprises'))
    form = EmailForm(request.form)
    if request.method == 'POST' and form.validate():
        email.email = form.email.data
        try:
            email.put()
            return redirect(url_for('admin.edit_enterprise', keyurl=email.enterprise))
        except CapabilityDisabledError:
            flash('save error')
    return render_template('admin.edit_email.html', form=form, keyurl=keyurl)


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
    return redirect(url_for('admin.edit_enterprise', keyurl=enterpris))


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
    mails = EmailModel.query()

    form.enterprise_mail.choices = [(mail.key.urlsafe(), mail.enterprise.get().name + ' -- ' + mail.email) for mail in mails]
    if request.method == 'POST' and form.validate():
        user = flask_login.current_user
        mail = ndb.Key(urlsafe=form.enterprise_mail.data)
        enterprise = mail.get().enterprise
        job = JobModel(
            title = form.title.data,
            type = form.type.data,
            enterprise = enterprise,
            enterprise_mail = mail,
            content = form.content.data,
       #     poster = user.key
        )
        try:
            job.put()
            return redirect(url_for('admin.jobs'))
        except CapabilityDisabledError:
            flash('add job error!')
    return render_template('admin/new_job.html', form=form)


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
    form.enterprise.choices = [(e.key.urlsafe(), e.name) for e in enterprises]
    if request.method == 'POST' and form.validate():
            job.title = form.title.data
            job.type = form.type.data
            job.enterprise = ndb.Key(urlsafe=form.enterprise.data)
            job.content = form.content.data
            try:
                job.put()
                return redirect(url_for('admin.jobs'))
            except CapabilityDisabledError:
                flash('error')
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

@admin.route('/')
def index():
    """
    """
    return render_template('base_admin.html')

def init_admin():
    role = ROLES['ADMIN']
    user = UserModel.query(UserModel.username=='admin').get()
    print user
    if user is None:
        #create admin
        admin = UserModel(
            username = 'admin',
            password = 'admin',
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
