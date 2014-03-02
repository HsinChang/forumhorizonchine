# from flask_admin import Admin, BaseView, expose

# class AdminView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/index.html')
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.ext import ndb
from flask import Blueprint, render_template, redirect, url_for,request, flash, Response
from forms import *
from models import *
from form2model import *
from decorators import admin_required
from application import app
from passlib.apps import custom_app_context as pwd_context
import flask_login
from flask_babel import format_date
from os.path import splitext
import re
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
            flash('login succeeded!', 'success')
        else:
            flash('login failed', 'error')
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
            flash('password changed!', 'info')
            redirect(url_for('admin.index'))
        except CapabilityDisabledError:
            flash('error whan changing password', 'error')
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
        flash('delete failed', 'error')
    redirect(url_for('amdin.users'))


@admin.route('/enterprises')
@admin_required
def enterprises():
    """
    """
    enterprises = EnterpriseModel.query().order(EnterpriseModel.order)
    return render_template('admin/enterprises.html', enterprises=enterprises)


@admin.route('/sort_enterprises', methods=['GET','POST'])
@admin_required
def sort_enterprises():
    """
    """
    enterprises = EnterpriseModel.query().order(EnterpriseModel.order)
    e_list = []
    for index, e in enumerate(enterprises):
        e.order = index
        e_list.append(e)

    if request.method == 'POST':
        order = get_order(request)
        reorder(e_list, order)
        ndb.put_multi(e_list)
        e_list.sort(key=lambda e: e.order)

    return render_template("admin/sort_enterprises.html", enterprises=e_list)


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
            flash('error', 'error')
    return render_template('admin/new_enterprise.html', form=form)


@admin.route('/edit_enterprise/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_enterprise(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    e = key.get()
    if not e:
        flash(_('no such enterprise'), 'error')
        return redirect(url_for('admin.enterprises'))
    emails = EmailModel.query(EmailModel.enterprise==e.key)
    form = BaseEnterpriseForm(request.form)

    if request.method == 'GET':
        form.name.data = e.name
        form.shortname.data = e.shortname

    elif request.method == 'POST' and form.validate():
        e.name = form.name.data
        e.shortname = form.shortname.data
        try:
            e.put()
            return redirect(url_for('admin.enterprises'))
        except CapabilityDisabledError:
            flash('error', 'error')
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
        flash(_('no such enterprise'), 'error')
        return redirect(url_for('admin.enterprises'))
    emails = EmailModel.query(EmailModel.enterprise==key)
    keys = [e.key for e in emails]

    try:
        ndb.delete_multi(keys)
        e.key.delete()
    except CapabilityDisabledError:
        flash(_('fail to delete'), 'error')
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
            flash('save error', 'error')
    return render_template('admin/new_email.html', form=form, keyurl=keyurl)


@admin.route('/edit_email/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_email(keyurl):
    email = ndb.Key(urlsafe=keyurl).get()
    if not email:
        flash('no such email', 'error')
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
            flash('save error', 'error')
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
        flash('no such email', 'error')
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
    grouped_jobs = {None:[]}
    incomplete_jobs = []
    jobs = JobModel.query()
    for job in jobs:
        if job.is_complete is False:
            grouped_jobs[None].append(job)
        elif job.enterprise in grouped_jobs:
            grouped_jobs[job.enterprise].append(job)
        else:
            grouped_jobs[job.enterprise] = [job]

    for jobs in grouped_jobs.values():
        jobs.sort(key=lambda job: job.order)

    return render_template('admin/jobs.html',
                           grouped_jobs=grouped_jobs)


@admin.route('/sort_jobs/<keyurl>', methods=['GET', 'POST'])
@admin_required
def sort_jobs(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    jobs = JobModel.query(JobModel.enterprise==key).order(JobModel.order)
    job_list = []
    for index, job in enumerate(jobs):
        job.order = index
        job_list.append(job)

    if request.method == 'POST':
        order = get_order(request)
        reorder(job_list, order)
        ndb.put_multi(job_list)
        job_list.sort(key=lambda j: j.order)
    return render_template('admin/sort_jobs.html', e=key.get(), jobs=jobs)

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
        flash('there is no enterprise, please create one before add new job', 'error')
        return redirect(url_for('admin.new_enterprise'))

    grouped_emails = {e.key.urlsafe(): [] for e in enterprises}
    for m in mails:
        key = m.enterprise.urlsafe()
        if key in grouped_emails:
            grouped_emails[key].append({'url': m.key.urlsafe(), 'email': m.email})

    form.enterprise_email.choices = [(i['url'], i['email']) for value in grouped_emails.values() for i in value]

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
            type=form.type.data,
            is_online=form.is_online.data,
            enterprise=enterprise,
            enterprise_email=mail,
            meta=meta,
            published=fr["published"] or en["published"] or zh["published"],
            default_lang=form.default_lang.data,
            cv_required=form.cv_required.data,
       #     poster = user.key
        )
        try:
            job.put()
            return redirect(url_for('admin.jobs'))
        except CapabilityDisabledError:
            flash('add job error!', 'error')
    return render_template('admin/new_job.html', form=form, grouped_emails = json.dumps(grouped_emails))


@admin.route('/edit_job/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_job(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    job = key.get()
    if not job:
        flash(_('no such job'), 'error')
        return redirect(url_for('admin.jobs'))
    form = JobForm(request.form, obj=job)
    enterprises = EnterpriseModel.query()
    mails = EmailModel.query()

    form.enterprise.choices = [(e.key.urlsafe(), e.name) for e in enterprises]
    grouped_emails = {e.key.urlsafe(): [] for e in enterprises}
    for m in mails:
        key = m.enterprise.urlsafe()
        if key in grouped_emails:
            grouped_emails[key].append({'url': m.key.urlsafe(), 'email': m.email})

    form.enterprise_email.choices = [(i['url'], i['email']) for value in grouped_emails.values() for i in value]

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

        job.published = job.meta['en']['published'] or job.meta['fr']['published'] or job.meta['zh']['published']
        job.default_lang = form.default_lang.data
        job.cv_required = form.cv_required.data
        try:
            job.put()
            return redirect(url_for('admin.jobs'))
        except CapabilityDisabledError:
            flash('error', 'error')
    elif request.method == 'GET':
        #GET handle goes here
        #in case of no enterprise when importing
        if job.enterprise:
            form.enterprise.data = job.enterprise.urlsafe()
            form.enterprise_email.choices = [(i['url'], i['email']) for i in grouped_emails[form.enterprise.data]]

        if job.is_online:
            form.is_online.data = True
            form.apply_url.data = job.apply_url
        else:
            form.is_online.data = False
            form.enterprise_email.data = job.enterprise_email.urlsafe()

        for lang in ['fr', 'en', 'zh']:
            v = getattr(form, "publish_"+lang)
            v.data = job.meta[lang]['published']

            v = getattr(form, "title_"+lang)
            v.data = job.meta[lang]['title']

            v = getattr(form, "content_"+lang)
            v.data = job.meta[lang]['content']

    return render_template('admin/edit_job.html', form=form, keyurl=keyurl, grouped_emails= json.dumps(grouped_emails))


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
        flash(_('no such job'), 'error')
        return redirect(url_for('admin.jobs'))
    try:
        job.key.delete()
    except CapabilityDisabledError:
        flash(_('fail to delete'), 'error')
    return redirect(url_for('admin.jobs'))


@admin.route('/forum', methods=["GET", "POST"])
@admin_required
def forum():
    forum = ForumModel.query().get()
    if not forum:
        forum = ForumModel()
    form = ForumForm(request.form, obj=forum)
    if request.method == 'POST' and form.validate():
        forum.date = form.date.data
        forum.address = form.address.data
        forum.registrable = form.registrable.data
        if forum.registrable:
            forum.register_link = form.register_link.data
        forum.put()
    return render_template('admin/forum.html', form=form)


@admin.route('/activities')
@admin_required
def activities():
    a = ActivityModel.query()
    return render_template('admin/activities.html', activities=a)

@admin.route('/new_activity', methods=['GET', 'POST'])
@admin_required
def new_activity():
    form = ActivityForm(request.form)
    if request.method == 'POST' and form.validate():
        meta = {}
        meta['en'] = {
            'title': form.title.data,
            'content': form.content.data
        }
        activity = ActivityModel(
            date = form.date.data,
            address = form.address.data,
            registrable = form.registrable.data,
            register_link = form.register_link.data,
            meta = meta
        )
        activity.put()
        return redirect(url_for('admin.activities'))
    return render_template('admin/new_activity.html', form=form)

@admin.route('/edit_activity/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_activity(keyurl):
    activity = ndb.Key(urlsafe=keyurl).get()
    if not activity:
        return redirect('admin.activities')
    form = ActivityForm(request.form, obj=activity)
    if request.method == 'GET':
        form.title.data = activity.meta['en']['title']
        form.content.data = activity.meta['en']['content']

    if request.method == 'POST' and form.validate():
        meta = {}
        meta['en'] = {
            'title': form.title.data,
            'content': form.content.data
        }
        activity.date = form.date.data
        activity.address = form.address.data
        activity.registrable = form.registrable.data
        activity.register_link = form.register_link.data
        activity.meta = meta

        activity.put()
        return redirect(url_for('admin.activities'))
    return render_template('admin/edit_activity.html', form=form, keyurl=keyurl)

@admin.route('/delete_activity/<keyurl>')
@admin_required
def delete_activity(keyurl):
    activity = ndb.Key(urlsafe=keyurl).get()
    activity.key.delete()
    return redirect(url_for('admin.activities'))

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
        flash('not xml file', 'error')
    content = f.read()
    Data.import_enterprise(content)
    flash('import success!', 'success')
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
        flash('not xml file', 'error')
    else:
        content = f.read()
        Data.import_jobs(content)
        flash('import success!', 'success')
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


@admin.route('/menus')
@admin_required
def menus():
    topmenu = MenuModel.query(MenuModel.type == 'TOP').order(MenuModel.order)
    return render_template('admin/menus.html', menus=menus, topmenu=topmenu)


def _init_menu_form(form):
    pages = PageModel.query()
    actions = [(page.id, page.id) for page in pages]
    # for rule in app.url_map.iter_rules():
    #     if "GET" in rule.methods and "POST" not in rule.methods:
    #         #url = url_for(rule.endpoint)
    #         actions.append((rule.endpoint, rule.endpoint))

    form.action.choices = actions


from views import add_menu_rule

@admin.route('/new_menu', methods=['GET', 'POST'])
@admin.route('/new_menu/<keyurl>', methods=['GET', 'POST'])
@admin_required
def new_menu(keyurl=None):
    form = MenuForm(request.form)
    _init_menu_form(form)
    if keyurl:
        parent = ndb.Key(urlsafe=keyurl).get()
    else:
        parent = None
    print(parent)
    if request.method == 'POST' and form.validate():
        menu = MenuModel()
        update_menu(menu, form)

        if parent:
            menu.parent = parent.key
            if parent.type == 'TOP':
                menu.type = 'SIDE_NAV'
                menu.action = None
            else:
                menu.type = 'SIDE_ENTRY'
        else:
            menu.parent = None
            menu.type = 'TOP'
        menu.put()
        if parent:
            parent.children.append(menu.key)
            parent.put()

        return redirect(url_for('admin.menus'))
    return render_template('admin/new_menu.html', form=form, keyurl=keyurl)


@admin.route('/edit_menu/<keyurl>', methods=["GET", "POST"])
@admin_required
def edit_menu(keyurl):
    menu = ndb.Key(urlsafe=keyurl).get()
    if menu:
        form = MenuForm(request.form, obj=menu)
        _init_menu_form(form)

        form.en.data = menu.meta['en']
        form.fr.data = menu.meta['fr']
        form.zh.data = menu.meta['zh']
        if request.method == 'POST' and form.validate():
            update_menu(menu, form)
            menu.put()
            return redirect(url_for('admin.menus'))
        return render_template('admin/edit_menu.html', form=form, keyurl=keyurl)
    else:
        abort(404)


def get_order(request):
    data = request.form['order']
    order = re.findall(r'\d+', data)
    order = [int(x) for x in order]
    return order


def reorder(items, order):
    for i in range(len(order)):
        rank = order[i]
        item = items[rank]
        item.order = i
    return items

@admin.route('/sort_menu', methods=['GET', 'POST'])
@admin.route('/sort_menu/<keyurl>', methods=['GET', 'POST'])
@admin_required
def sort_menu(keyurl=None):
    menu = None
    if keyurl:
        menu = ndb.Key(urlsafe=keyur).get()
        if not menu:
            abort(404)
            children = ndb.get_multi(menu.children)
            children.sort(key=lambda m: m.order)

    else:
        children = MenuModel.query(MenuModel.type=="TOP").order(MenuModel.order)

    menu_list = []
    for index, menu in enumerate(children):
        menu.order = index
        menu_list.append(menu)
    if request.method == 'POST':
        order = get_order(request)
        reorder(menu_list, order)
        ndb.put_multi(menu_list)
        menu_list.sort(key=lambda m: m.order)

    if menu:
        menu.children = [m.key for m in menu_list]
        menu.put()
    return render_template('admin/sort_menus.html',
                           menus=menu_list, keyurl=keyurl)


@admin.route('/delete_menu/<keyurl>')
@admin_required
def delete_menu(keyurl):
    def _delete_children(menu):
        children = menu.children.get()
        for child in children:
            _delete_children(child.get())
            menu.delete()

    key = ndb.Key(urlsafe=keyurl)
    menu = key.get()
    if menu.parent:
        parent = menu.parent.get()
        parent.children.remove(menu.key)
        parent.put()

    if menu.children:
        children = ndb.get_multi(menu.children)
        for child in children:
            _delete_children(child.get())
    key.delete()

    return redirect(url_for('admin.menus'))


@admin.route('/pages')
@admin_required
def pages():
    pages = PageModel.query()
    return render_template('admin/pages.html', pages=pages)


@admin.route('/new_page', methods=['GET', 'POST'])
@admin_required
def new_page():
    form = PageForm(request.form)

    if request.method == 'POST' and form.validate():
        page = PageModel()
        update_page(page, form)
        page.put()
        return redirect(url_for('admin.pages'))
    return render_template('admin/new_page.html', form=form)

@admin.route('/edit_page/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_page(keyurl):
    page = ndb.Key(urlsafe=keyurl).get()
    if page:
        form = PageForm(request.form, obj=page)
        form.title_en.data = page.meta['en']['title']
        form.title_fr.data = page.meta['fr']['title']
        form.title_zh.data = page.meta['zh']['title']
        form.content_en.data = page.meta['en']['content']
        form.content_fr.data = page.meta['fr']['content']
        form.content_zh.data = page.meta['zh']['content']
        if request.method == 'POST' and form.validate():
            update_page(page, form)
            page.put()
            return redirect(url_for('admin.pages'))

        return render_template('admin/edit_page.html', form=form, keyurl=keyurl)
    else:
        abort(404)


@admin.route('/delete_page/<keyurl>')
@admin_required
def delete_page(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    modules = ModuleModel.query(ModuleModel.page == key)
    key.delete()
    ndb.delete_multi([m.key for m in modules])
    return redirect(url_for('admin.pages'))


@admin.route('/page_modules/<keyurl>')
@admin_required
def page_modules(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    modules = ModuleModel.query(ModuleModel.page == key)
    return render_template('admin/page_modules.html', modules=modules, keyurl=keyurl)


from modules import MODULES
@admin.route('/page_modules/new/<keyurl>', methods=['GET', 'POST'])
@admin_required
def new_page_module(keyurl):
    key = ndb.Key(urlsafe=keyurl)
    form = ModuleForm(request.form)
    form.name.choices = [(i, i) for i in MODULES.iterkeys()]
    if request.method == 'POST' and form.validate():
        module = ModuleModel()
        module.page = key
        module.name = form.name.data
        module.position = form.position.data
        module.put()
        return redirect(url_for('admin.page_modules', keyurl=keyurl))
    return render_template('admin/new_page_module.html',
                           form=form, keyurl=keyurl)


@admin.route('/page_modules/edit/<keyurl>', methods=['GET', 'POST'])
@admin_required
def edit_page_module(keyurl):
    module = ndb.Key(urlsafe=keyurl).get()
    form = ModuleForm(request.form, obj=module)
    form.name.choices = [(i, i) for i in MODULES.iterkeys()]
    if request.method == 'POST' and form.validate():
        module.name = form.name.data
        module.position = form.position.data
        module.put()
        page = module.page
        return redirect(url_for('admin.page_modules', keyurl=page.urlsafe()))
    return render_template('admin/edit_page_module.html',
                           form=form, keyurl=keyurl)


@admin.route('/page_modules/delete/<keyurl>')
@admin_required
def delete_page_module(keyurl):
    key = ndb.Key(urlsafe=keyurl).get()
    module = key.get()
    page = module.page
    key.delete()
    return redirect(url_for('admin.page_modules', keyurl=page.urlsafe()))


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
