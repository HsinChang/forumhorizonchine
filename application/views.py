"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect, session

from flask_cache import Cache
from flask_babel import refresh
import flask_login
from application import app
from decorators import login_required, admin_required
from forms import RegisterForm, JobForm
from models import ExhibitorModel, JobModel


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/setlocale/<locale>')
def setlocale(locale):
    session['locale'] = locale
    refresh()
    return redirect(request.referrer)

#about
@app.route('/about/access')
def access():
    return render_template('about/access.html')

@app.route('/about/balance')
def balance():
    return render_template('about/balance.html')

@app.route('/about/contact')
def contact():
    return render_template('about/contact.html')

@app.route('/about')
def about():
    return redirect(url_for('access'))

#visitors
@app.route('/visitors/inscript')
def inscript():
    return render_template('inscription/forum2013.html')
#    return render_template('visitors/inscription.html')

@app.route('/visitors/program')
def program():
    return render_template('visitors/program.html')

@app.route('/visitors/exhibitors')
def visitors_exhibitors():
    return render_template('visitors/exhibitors.html')

@app.route('/visitors/job')
def job():
    return render_template('visitors/job.html')

@app.route('/visitors/workpermit')
def workpermit():
    return render_template('visitors/workpermit.html')

@app.route('/visitors')
def visitors():
    return redirect(url_for('program'))

#exhibitors
@app.route('/exhibitors/register', methods=['GET', 'POST'])
def exhibitors_register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        exhibitor = ExhibitorModel(
            username = form.username.data,
            password = form.password.data,
            email = form.email.data,
            entreprise = form.entreprise.data
        )
        app.logger.debug(exhibitor.username)
        try:
            exhibitor.put()
            return redirect(url_for('exhibitors'))
        except CapabilityDisabledError:
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)

@app.route('/exhibitors/login', methods=['GET', 'POST'])
def exhibitors_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        exhibitor = ExhibitorModel.query(ExhibitorModel.username==username, ExhibitorModel.password==password).get()
        if exhibitor:
            result = flask_login.login_user(exhibitor)
    return redirect(url_for('exhibitors'))

@app.route('/exhibitors/logout')
def exhibitors_logout():
    flask_login.logout_user()
    return redirect(url_for('exhibitors'))

@app.route('/exhibitors/offres')
def exhibitors_jobs():
    user = flask_login.current_user
    jobs = JobModel.query(JobModel.poster == user.key)
    return render_template('exhibitors/offres.html', jobs=jobs)

@app.route('/exhibitors/new_offre', methods=['GET', 'POST'])
def new_job():
    form = JobForm(request.form)
    app.logger.debug(form.validate())
    app.logger.debug(form.errors)
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
            return redirect(url_for('exhibitors_jobs'))
        except CapabilityDisabledError:
            return render_template('exhibitors/new_job.html', form=form)
    return render_template('exhibitors/new_job.html', form=form)

@app.route('/exhibitors/edit_job')
def edit_job():
    return 'edit_job'

@app.route('/exhibitors/delete_job')
def delete_job():
    return 'delete_job'

@app.route('/exhibitors/visitors')
def exhibitors_visitors():
    return render_template('exhibitors/visitors.html')

@app.route('/exhibitors/services')
def services():
    return render_template('exhibitors/services.html')

@app.route('/exhibitors')
def exhibitors():
    return redirect(url_for('exhibitors_visitors'))


@login_required
def list_examples():
    """List all examples"""
    examples = ExampleModel.query()
    form = ExampleForm()
    if form.validate_on_submit():
        example = ExampleModel(
            example_name=form.example_name.data,
            example_description=form.example_description.data,
            added_by=users.get_current_user()
        )
        try:
            example.put()
            example_id = example.key.id()
            flash(u'Example %s successfully saved.' % example_id, 'success')
            return redirect(url_for('list_examples'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('list_examples'))
    return render_template('list_examples.html', examples=examples, form=form)


@login_required
def edit_example(example_id):
    example = ExampleModel.get_by_id(example_id)
    form = ExampleForm(obj=example)
    if request.method == "POST":
        if form.validate_on_submit():
            example.example_name = form.data.get('example_name')
            example.example_description = form.data.get('example_description')
            example.put()
            flash(u'Example %s successfully saved.' % example_id, 'success')
            return redirect(url_for('list_examples'))
    return render_template('edit_example.html', example=example, form=form)


@login_required
def delete_example(example_id):
    """Delete an example object"""
    example = ExampleModel.get_by_id(example_id)
    try:
        example.key.delete()
        flash(u'Example %s successfully deleted.' % example_id, 'success')
        return redirect(url_for('list_examples'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('list_examples'))


@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


@cache.cached(timeout=60)
def cached_examples():
    """This view should be cached for 60 sec"""
    examples = ExampleModel.query()
    return render_template('list_examples_cached.html', examples=examples)


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''
