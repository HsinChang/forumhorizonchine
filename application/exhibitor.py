from flask import Blueprint, render_template, redirect, url_for, request
from forms import RegisterForm, JobForm
from models import ExhibitorModel, JobModel
import flask_login
exhibitor = Blueprint('exhibitor', __name__)

@exhibitor.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        exhibitor = ExhibitorModel(
            username = form.username.data,
            password = form.password.data,
            email = form.email.data,
            entreprise = form.entreprise.data
        )
        try:
            exhibitor.put()
            return redirect(url_for('exhibitor.index'))
        except CapabilityDisabledError:
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)

@exhibitor.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        exhibitor = ExhibitorModel.query(ExhibitorModel.username==username, ExhibitorModel.password==password).get()
        if exhibitor:
            result = flask_login.login_user(exhibitor)
    return redirect(url_for('exhibitor.index'))

@exhibitor.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('exhibitor.index'))

@exhibitor.route('/offres')
def jobs():
    user = flask_login.current_user
    jobs = JobModel.query(JobModel.poster == user.key)
    return render_template('exhibitors/offres.html', jobs=jobs)

@exhibitor.route('/new_offre', methods=['GET', 'POST'])
def new_job():
    form = JobForm(request.form)
    if request.method == 'POST' and form.validate():
        user = flask_login.current_user
        job = JobModel(
            title = form.title.data,
            type = form.type.data,
            content = form.content.data,
            poster = user.key
        )
        try:
            job.put()
            return redirect(url_for('exhibitor.jobs'))
        except CapabilityDisabledError:
            return render_template('exhibitors/new_job.html', form=form)
    return render_template('exhibitors/new_job.html', form=form)

@exhibitor.route('/edit_job')
def edit_job():
    return 'edit_job'

@exhibitor.route('/delete_job')
def delete_job():
    return 'delete_job'

@exhibitor.route('/visitors')
def visitors():
    return render_template('exhibitors/visitors.html')

@exhibitor.route('/services')
def services():
    return render_template('exhibitors/services.html')

@exhibitor.route('/')
def index():
    return redirect(url_for('exhibitor.visitors'))
