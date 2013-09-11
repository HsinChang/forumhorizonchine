# from flask_admin import Admin, BaseView, expose

# class AdminView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/index.html')
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.ext import ndb
from flask import Blueprint, render_template, redirect, url_for, request, flash
from forms import RegisterForm, JobForm, EnterpriseForm
from models import UserModel, JobModel, ROLES, EnterpriseModel
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
def logout():
    """
    logout admin
    """
    flask_login.logout_user()
    return redirect(url_for('admin.index'))

@admin.route('/users')
def users():
    """
    user management
    """
    users = UserModel.query()
    return render_template('admin/users.html', users=users)

@admin.route('/enterprises')
def enterprises():
    """
    """
    enterprises = EnterpriseModel.query()
    return render_template('admin/enterprises.html', enterprises=enterprises)

@admin.route('/new_enterprise', methods=['GET', 'POST'])
def new_enterprise():
    """
    """
    form = EnterpriseForm(request.form)
    if request.method == 'POST' and form.validate():
        e = EnterpriseModel(
            name = form.name.data,
            shortname = form.shortname.data,
            email = form.email.data
        )
        try:
            e.put()
            return redirect(url_for('admin.enterprises'))
        except CapabilityDisabledError:
            flash('error')
    return render_template('admin/new_enterprise.html', form=form)

@admin.route('/edit_enterprise/<keyurl>', methods=['GET', 'POST'])
def edit_enterprise(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    e = key.get()
    if not e:
        flash(_('no such enterprise'))
        return redirect(url_for('admin.enterprises'))
    form = EnterpriseForm(request.form, obj=e)
    if request.method == 'POST' and request.validate():
            e.name = form.name.data
            e.shortname = form.shortname.data
            e.email = form.email.data
            try:
                e.put()
                return redirect(url_for('admin.enterprises'))
            except CapabilityDisabledError:
                flash('error')
    return render_template('admin/edit_enterprise.html', form=form, keyurl=keyurl)


@admin.route('/delete_enterprise/<keyurl>')
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
    try:
        e.key.delete()
    except CapabilityDisabledError:
        flash(_('fail to delete'))
    return redirect(url_for('admin.enterprises'))


@admin.route('/jobs')
def jobs():
    """
    all jobs
    """
    jobs = JobModel.query()
    return render_template('admin/jobs.html', jobs=jobs)

@admin.route('/new_job', methods=['GET', 'POST'])
def new_job():
    """
    create new job infos
    """
    form = JobForm(request.form)
    enterprises = EnterpriseModel.query()
    form.enterprise.choices = [(e.key.urlsafe(), e.name) for e in enterprises]
    if request.method == 'POST' and form.validate():
        user = flask_login.current_user
        job = JobModel(
            title = form.title.data,
            type = form.type.data,
            enterprise = ndb.Key(urlsafe=form.enterprise.data),
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
