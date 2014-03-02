"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect, session, abort

from flask_cache import Cache
from flask_babel import refresh, format_date
import flask_login

from application import app
from decorators import login_required, admin_required
from forms import RegisterForm, JobForm, BaseContactForm
from models import ForumModel, PageModel, MenuModel, ModuleModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

# @app.route('/')
# def home():
#     forum = ForumModel.query().get()
#     if not forum:
#         forum = ForumModel(
#             date = '',
#             address = ''
#         )
#     forum.formated_date = format_date(forum.date, 'full')
#     return render_template('home.html', forum=forum)

@app.route('/')
def home():
    return redirect(url_for('page', entry='index'))

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
    locale = session['locale']
    return render_template('about/balance.html', usertype=usertype, locale=locale)

@app.route('/<usertype>/about/contact', methods=['GET', 'POST'])
def contact(usertype):
    form = BaseContactForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        comment = form.message.data

        sender= app.config['SENDER']
        to= app.config['CONTACTUS']
        subject = 'Message from {0} {1}<{2}>'.format(first_name, last_name, email)
        body = u"""
    Following is the message from {0} {1} {2}:

    {3}
    """.format(first_name, last_name, email, comment)

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

from modules import MODULES
@app.route('/<entry>')
@app.route('/<root>/<entry>')
def page(entry="", root=""):
    menu = None
    if root == "":
        menu = MenuModel.query(MenuModel.id == entry).get()
    else:
        menus = MenuModel.query(MenuModel.id == entry)
        for m in menus:
            top = _top(m)
            if top == root:
                menu = m
                break

    if menu:
        page = PageModel.query(PageModel.id == menu.action).get()
        modules = ModuleModel.query(ModuleModel.page == page.key)
        module_content = {}
        for module in modules:
            f = MODULES[module.name]
            content = f()
            if module.position not in module_content:
                module_content[module.position] = []
            module_content[module.position].append(content)

        if page.type == 'SINGLE':
            return render_template('base_page_1.html',
                                   page=page, modules=module_content)
        elif page.type == 'SIDEBAR':
            return render_template('base_page_2.html', page=page,
                                   topmenu=_top(menu), modules=module_content)
    else:
        abort(404)

# @app.route('/page/<keyurl>')
# def page(keyurl):
#     menu = ndb.Key(urlsafe=keyurl).get()
#     if menu:
#         page = PageModel.query(PageModel.id == menu.action).get()
#         modules = ModuleModel.query(ModuleModel.page == page.key)
#         module_content = {}
#         for module in modules:
#             f = MODULES[module.name]
#             content = f()
#             if module.position not in module_content:
#                 module_content[module.position] = []
#             module_content[module.position].append(content)

#         if page.type == 'SINGLE':
#             return render_template('base_page_1.html',
#                                    page=page, modules=module_content)
#         elif page.type == 'SIDEBAR':
#             return render_template('base_page_2.html', page=page,
#                                    topmenu=_top(menu), modules=module_content)
#     else:
#         abort(404)


def page_view_function(page, topmenu):
    def page_view():
        return render_template('base_page.html', page=page, topmenu=topmenu)
    return page_view


def generate_rule(prefix, menu, top):
    url = prefix + menu.id
    if menu.action:
        page = PageModel.query(PageModel.id == menu.action).get()
        f = page_view_function(page, top)
        app.add_url_rule(url, url[1:], f)

    for child in menu.children:
        submenu = child.get()
        generate_rule(url+'/', submenu, top)


def _top(menu):
    if menu.parent:
        return _top(menu.parent.get())
    else:
        return menu


def add_menu_rule(menu):
    endpoint = menu_endpoint(menu)
    page = PageModel.query(PageModel.id == menu.action).get()
    f = page_view_function(page, _top(menu))
#    app.add_url_rule('/'+endpoint, endpoint, f)



def init_pages_rule():
    pass
    # topmenu = MenuModel.query(MenuModel.type == 'TOP')
    # for menu in topmenu:
#        generate_rule('/', menu, menu)


def menu_endpoint(menu):
    def _join_endpoint(menu, postfix):
        if menu.parent:
            return _join_endpoint(menu.parent, menu.id + '/' + postfix)
        else:
            return menu.id + '/' + postfix
    return _join_endpoint(menu, '')
