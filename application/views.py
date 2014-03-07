"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect, session

from flask_cache import Cache
from flask_babel import refresh, format_date
import flask_login

from application import app, get_locale
from decorators import login_required, admin_required
from forms import RegisterForm, JobForm, BaseContactForm
from models import ForumModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/')
def home():
    forum = ForumModel.query().get()
    if not forum:
        forum = ForumModel(
            date = '',
            address = ''
        )
    forum.formated_date = format_date(forum.date, 'full')
    return render_template('home.html', forum=forum)

@app.route('/setlocale/<locale>')
def setlocale(locale):
    session['locale'] = locale
    refresh()
    return redirect(request.referrer)

#about
@app.route('/<usertype>/about/access')
def access(usertype):
    return render_template('about/access.html', usertype=usertype)

@app.route('/<usertype>/about/balance')
def balance(usertype):
    locale = get_locale()
    return render_template('about/balance.html', usertype=usertype, locale=locale)

@app.route('/<usertype>/about/contact', methods=['GET', 'POST'])
def contact(usertype):
    form = BaseContactForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        comment = form.message.data

        sender= app.config['SENDER']
        to= app.config['CONTACT']
        subject = 'Message from {0}'.format(email)
        body = u"""
    Following is the message from {0}:

    {1}
    """.format(email, comment)

        mail.send_mail(sender, to, subject, body, reply_to=email)

        flash('mail sent')
    return render_template('about/contact.html', form=form, usertype=usertype)

@app.route('/<usertype>/about')
def about(usertype):
    return redirect(url_for('access', usertype=usertype))

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
