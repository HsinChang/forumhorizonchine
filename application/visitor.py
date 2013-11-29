# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import JobModel, EnterpriseModel, EmailModel
from forms import ContactForm
from flask_mail import Message
from application import app
from google.appengine.api import mail
from google.appengine.ext import ndb
from os.path import splitext, getsize
from operator import itemgetter

visitor = Blueprint('visitor', __name__)

#visitors
@visitor.route('/inscription')
def inscription():
    return render_template('visitors/inscription.html')


@visitor.route('/program')
def program():
    return render_template('visitors/program.html')


@visitor.route('/exhibitors')
def exhibitors():
    return render_template('visitors/exhibitors.html')


@visitor.route('/job')
def job():
    grouped_jobs = {}
    jobs = JobModel.query(JobModel.published==True, JobModel.is_complete==True)
    for job in jobs:
        locale = session['locale']
        if job.meta[locale]["published"] == True:
            job.current_lang = locale
        else:
            job.current_lang = job.default_lang
        job.current = job.meta[job.current_lang]

        if job.enterprise in grouped_jobs:
            grouped_jobs[job.enterprise].append(job)
        else:
            grouped_jobs[job.enterprise] = [job]

        tuple_jobs = sorted(grouped_jobs.items(), key=itemgetter(1))
    return render_template('visitors/job.html', grouped_jobs=tuple_jobs, languages = app.config['LANGUAGES'])



@visitor.route('/workpermit', methods=['GET', 'POST'])
def workpermit():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        comment = form.message.data

        subject = 'Comment about the workpermit guide from {0} {1}<{2}>'.format(first_name, last_name, email)
        body = u"""
        Following is the comment from {0} {1} {2}:

        {3}
        """.format(first_name, last_name, email, comment)

        mail.send_mail('Admin of AFCP <lutianming1005@gmail.com>',
                       "lutianming1005@hotmail.com",
                       subject,
                       body)
        flash('mail sent')
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
    lang = request.form['lang']
    email_enterprise = request.form['email.to']
    email_to = ndb.Key(urlsafe=email_enterprise)

    to = email_to.get().email
    # to = 'lutianming1005@hotmail.com'

    enterprise = request.form['enterprise']
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    files = []

    for k, f in request.files.items():
        path, ext = splitext(f.filename)
        if ext != '.doc' and ext != '.docx' and ext != '.pdf':
            flash('only support doc and pdf files')
            return redirect(url_for('visitor.job'))
        # if getsize(f.stream) > max_size:
        #     flash('document size should be under 2M')
        #     return redirect(url_for('visitor.job'))

        f.filename = k + ext
        files.append(f)

    # if 'cv_en' in request.files:
    #     f = request.files['cv_en']
    #     path, ext = splitext(f.filename)
    #     f.filename = 'cv_en' + ext
    #     cv['en'] = f
    # if 'cv_fr' in request.files:
    #     f = request.files['cv_fr']
    #     path, ext = splitext(f.filename)
    #     f.filename = 'cv_fr' + ext
    #     cv['fr'] = request.files['cv_fr']
    # if 'cv_zh' in request.files:
    #     f = request.files['cv_zh']
    #     path, ext = splitext(f.filename)
    #     f.filename = 'cv_zh' + ext
    #     cv['zh'] = request.files['cv_zh']
    # lm = request.files['lm']
    attachments = []
    for f in files:
        attachments.append((f.filename, f.read()))

    sender = 'Admin of AFCP <lutianming1005@gmail.com>'
    cc = app.config['ADMIN']
    subject_en = 'New application sent by AFCP'
    subject_zh = u'来自AFCP的新职位申请'
    subject_fr = u'Une nouvelle candidatur envoyée par AFCP'
    subjects = {'en': subject_en, 'zh': subject_zh, 'fr': subject_fr}
    body_en = u"""
    Dear Sir/Miss,

    A new application for the position {0} has been sent through the Site of AFCP where the offre is published.

    Please have a look at the attached CV and cover letters of {1} {2} for this application. You can reach him/her with the email address {3}

    Best regards，
    The team of AFCP
    """
    body_zh = u"""
    您好，

    AFCP发给了您一份{0}这一职位的新申请。

    请查看附件中申请人{0} {1}的CV和动机信。您可以通过这一邮箱地址 {3} 与他/她取得联系。

    此致！
    AFCP团队
    """
    body_fr = u"""
    Madame, Monsieur,

    Une nouvelle candidature pour le poste {0} a été envoyée par l'intermédiaire du site de l'AFCP, l'offre y étant publiée.

    Veuillez trouver ci-joint le CV et la lettre de motivation de {1} {2} pour cette candidature. Vous pouvez le joindre à l'adresse e-mail {3}

    Bien à vous,

    L'équipe AFCP
    """
    bodies = {'en': body_en, 'zh': body_zh, 'fr': body_fr}

    subject = subjects[lang]
    body = bodies[lang].format(jobname, first_name, last_name, email)
    mail.send_mail(sender, to, subject, body, attachments=attachments, cc=cc)

    flash('mail sent')
    return redirect(url_for('visitor.job'))
