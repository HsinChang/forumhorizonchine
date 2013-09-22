from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.ext import ndb
from flask import Blueprint, render_template, redirect, url_for, request, flash
from forms import RegisterForm, JobForm
from models import UserModel, JobModel, ROLES
from decorators import login_required
from application import app
import flask_login
exhibitor = Blueprint('exhibitor', __name__)

@exhibitor.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = ExhibitorModel(
            username = form.username.data,
            password = form.password.data,
            role = ROLES['EXHIBITOR'],
            email = form.email.data,
            company = form.company.data
        )
        try:
            user.put()
            flash(_('registered'))
            return redirect(url_for('exhibitor.index'))
        except CapabilityDisabledError:
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)

@exhibitor.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserModel.query(UserModel.username==username, UserModel.password==password).get()
        if user and user.role == ROLES['EXHIBITOR']:
            result = flask_login.login_user(user)
    return redirect(url_for('exhibitor.index'))

@exhibitor.route('/logout')
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('exhibitor.index'))

@exhibitor.route('/jobs')
@login_required
def jobs():
    user = flask_login.current_user
    jobs = JobModel.query(JobModel.poster == user.key)
    return render_template('exhibitors/jobs.html', jobs=jobs)

@exhibitor.route('/new_job', methods=['GET', 'POST'])
@login_required
def new_job():
    form = JobForm(request.form)
    enterprises = EnterpriseModel.query()
    form.enterprises.choices = [(e.key.urlsafe(), e.name) for e in enterprise]
    if request.method == 'POST' and form.validate():
        user = flask_login.current_user
        job = JobModel(
            title = form.title.data,
            type = form.type.data,
            enterprise = ndb.Key(form.enterprise.data),
            content = form.content.data,
            poster = user.key
        )
        try:
            job.put()
            return redirect(url_for('exhibitor.jobs'))
        except CapabilityDisabledError:
            return render_template('exhibitors/new_job.html', form=form)
    return render_template('exhibitors/new_job.html', form=form)


@exhibitor.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = JobModel.get_by_id(int(job_id))
    if not job:
        flash(_('no such job'))
        return redirect(url_for('exhibitor.jobs'))
    form = JobForm(request.form, obj=job)
    if request.method == 'POST' and form.validate():
        try:
            job.title = form.title.data
            job.type = form.type.data
            job.enterprise = ndb.key(form.enterprise.data)
            job.content = form.content.data
            job.put()
            flash('job modified successfully!')
        except CapabilityDisabledError:
            flash('fail to modify job')
    return render_template('exhibitors/edit_job.html', form=form, job=job)

@exhibitor.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    job = JobModel.get_by_id(int(job_id))
    if not job:
        flash(_('no such job'))
        return redirect(url_for('exhibitor.jobs'))
    try:
        job.key.delete()
        flash(_('job deleted'))
    except CapabilityDisabledError:
        flash(_('fail to delete'))
    return redirect(url_for('exhibitor.jobs'))

@exhibitor.route('/visitors')
def visitors():
    return render_template('exhibitors/visitors.html')

@exhibitor.route('/services')
def services():
    return render_template('exhibitors/services.html')

@exhibitor.route('/')
def index():
    return redirect(url_for('exhibitor.visitors'))
