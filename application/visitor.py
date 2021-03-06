# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import JobModel, EnterpriseModel, EmailModel, ForumModel, ActivityModel
from forms import ContactForm
from flask_mail import Message
from flask_babel import lazy_gettext
from application import app, get_locale
from google.appengine.api import mail
from google.appengine.ext import ndb
from os.path import splitext, getsize
import itertools
from collections import defaultdict

visitor = Blueprint('visitor', __name__)

#visitors
@visitor.route('/inscription')
def inscription():
    forum = ForumModel.query().get()
    registrable = False
    link = None
    if forum and forum.registrable:
        registrable = True
        link = forum.register_link
    return render_template('visitors/inscription.html', registrable=registrable, link=link)


@visitor.route('/inscript/<keyurl>')
def inscript(keyurl):
    activity = ndb.Key(urlsafe=keyurl).get()
    if not activity:
        flash("unable to register")
        return redirect(url_for('visitor.activities'))
    return render_template('visitors/inscript.html', activity=activity)

@visitor.route('/program')
def program():
    return render_template('visitors/program.html')


@visitor.route('/exhibitors')
def exhibitors():
    return render_template('visitors/exhibitors.html')


@visitor.route('/job')
def job():
    jobs = JobModel.query(JobModel.published==True,
                          JobModel.is_complete==True)

    grouped_jobs = defaultdict(list)
    for job in jobs:
        locale = get_locale()
        if job.meta[locale]["published"] == True:
            job.current_lang = locale
        else:
            job.current_lang = job.default_lang
        job.current = job.meta[job.current_lang]
        grouped_jobs[job.enterprise].append(job)

    if len(grouped_jobs) == 0:
        grouped_jobs = None
    else:
        grouped_jobs = sorted(grouped_jobs.items(),
                              key=lambda i: i[0].get().order)

    return render_template('visitors/job.html',
                           grouped_jobs=grouped_jobs,
                           languages=app.config['LANGUAGES'])


@visitor.route('/activities')
def activities():
    a = ActivityModel.query()
    return render_template('visitors/activities.html', activities=a)


@visitor.route('/workpermit', methods=['GET', 'POST'])
def workpermit():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        comment = form.message.data

        sender = app.config['SENDER']
        to = app.config['CONTACT']
        subject = 'Comment about the workpermit guide from {0} {1}<{2}>'.format(first_name, last_name, email)
        body = u"""
        Following is the comment from {0} {1} {2}:

        {3}
        """.format(first_name, last_name, email, comment)

        mail.send_mail(sender,
                       to,
                       subject,
                       body)
        flash('mail sent', 'success')
    return render_template('visitors/workpermit.html', form=form)


@visitor.route('/infos')
def infos():
    return render_template('visitors/infos.html')


@visitor.route('/')
def index():
    return redirect(url_for('visitor.program'))


@visitor.route('/apply', methods=['POST'])
def apply():
    """
    """
    # joburl = request.form['joburl']
    # key = ndb.Key(urlsafe=joburl)
    # job = key.get()
    jobname = request.form['jobname']
    joburl = request.form['joburl']
    lang = request.form['lang']

    job = ndb.Key(urlsafe=joburl).get()
    mails_to = []
    for m in job.enterprise_email:
        v = m.get().email
        mails_to.append(v)

    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    files = []

    for k, f in request.files.items():
        path, ext = splitext(f.filename)
        if ext != '.doc' and ext != '.docx' and ext != '.pdf':
            flash('only support doc and pdf files', 'error')
            return redirect(url_for('visitor.job'))
        # if getsize(f.stream) > max_size:
        #     flash('document size should be under 2M')
        #     return redirect(url_for('visitor.job'))

        f.filename = u"{0}({1}){2}".format(k, path, ext)
        files.append(f)

    attachments = []
    for f in files:
        attachments.append((f.filename, f.read()))

    sender = app.config['SENDER']
    cc = app.config['CC']
    subject_en = 'New application sent by the site of AFCP'
    subject_zh = u'来自AFCP网站的新职位申请'
    subject_fr = u"Une nouvelle candidature envoyée par  le site de l'AFCP"
    subjects = {'en': subject_en, 'zh': subject_zh, 'fr': subject_fr}
    body_en = u"""
    <html>
    <p>Dear Sir/Miss,<p>

    <p>A new application for the position <b>{0}</b> has been sent through the Site of AFCP where the offre is published.</p>

    <p>Please have a look at the attached CV and cover letters of <b>{1} {2}</b> for this application. You can reach him/her with the email address <a href="mailto:{3}">{3}</a>.</p>

    <p>Best regards，</p>
    <p>The team of AFCP</p>
    </html>
    """
    body_zh = u"""
    <html>
    <p>您好，</p>

    <p>AFCP发给了您一份<b>{0}</b>这一职位的新申请。</p>

    <p>请查看附件中申请人<b>{1} {2}</b>的CV和动机信。您可以通过这一邮箱地址 <a href="mailto:{3}">{3}</a>与他/她取得联系。</p>

    <p>此致！</p>
    <p>AFCP团队</p>
    </html>
    """
    body_fr = u"""
    <html>
    <p>Madame, Monsieur,</p>

    <p>Une nouvelle candidature pour le poste <b>{0}</b> a été envoyée par l'intermédiaire du site de l'AFCP, l'offre y étant publiée.</p>

    <p>Veuillez trouver ci-joint le CV et la lettre de motivation de <b>{1} {2}</b> pour cette candidature. Vous pouvez le/la joindre à l'adresse e-mail <a href="mailto:{3}">{3}</a>.</p>

    <p>Bien à vous,</p>
    <p>L'équipe AFCP</p>
    </html>
    """
    bodies = {'en': body_en, 'zh': body_zh, 'fr': body_fr}

    subject = subjects[lang]
    body = bodies[lang].format(jobname, first_name, last_name, email)

    message = mail.EmailMessage(sender=sender)
    message.to = mails_to
    message.cc = cc
    message.subject = subject
    # message.html = render_template('mail/apply.html',
    #                                title=jobname,
    #                                first_name=first_name,
    #                                last_name=last_name,
    #                                email=email)
    message.html = body
    if attachments:
        message.attachments = attachments
    message.send()

    _apply_feedback(email, jobname)

    feedback = """
    your application is sent,
    please wait for the entreprise to contact with you
    """

    flash(feedback, 'success')
    return redirect(url_for('visitor.job'))


def _apply_feedback(email, jobname):
    sender = app.config['SENDER']
    m = mail.EmailMessage()
    m.sender = sender
    m.to = email
    m.subject = "your application is sent successfully"
    m.html = u"""
    <html>
    <p>Dear Sir/Miss,<p>

    <p>Your application for the position <b>{0}</b> has been sent to the entreprise</p>

    <p>Please wait for the entreprise to contact with you!</p>

    <p>Best regards，</p>
    <p>The team of AFCP</p>
    </html>
    """.format(jobname)
    m.send()
    return True
