# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import JobModel, EnterpriseModel, EmailModel
from flask_mail import Message
from application import app
from google.appengine.api import mail
from google.appengine.ext import ndb
from os.path import splitext, getsize

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
    jobs = JobModel.query(JobModel.published==True)
    for job in jobs:
        locale = session['locale']
        if locale == 'fr' and job.fr.published:
            job.default = job.fr
        elif locale == 'zh' and job.zh.published:
            job.default = job.zh
        elif locale == 'en' and job.en.published:
            job.default = job.en
        else:
            job.default = getattr(job, job.default_lang)

        if job.enterprise in grouped_jobs:
            grouped_jobs[job.enterprise].append(job)
        else:
            grouped_jobs[job.enterprise] = [job]
    return render_template('visitors/job.html', grouped_jobs=grouped_jobs)


@visitor.route('/workpermit')
def workpermit():
    return render_template('visitors/workpermit.html')


@visitor.route('/')
def index():
    return redirect(url_for('visitor.program'))


@visitor.route('/apply', methods=['POST'])
def apply():
    """
    """
    email_enterprise = request.form['email.to']
    email_to = ndb.Key(urlsafe=email_enterprise)
    jobname = request.form['jobname']
    enterprise = request.form['enterprise']
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    cv = {}

    #validate form
    if len(first_name) == 0 or len(last_name) == 0 or len(email) == 0:
        flash('empty field')
        return redirect(url_for('visitor.job'))

    #max size 2MB
    max_size = 2*1024*1024
    for k, f in request.files.items():
        print(k, f)
        path, ext = splitext(f.filename)
        print(path, ext)
        if ext != '.doc' and ext != '.docx' and ext != '.pdf':
            flash('only support doc and pdf files')
            return redirect(url_for('visitor.job'))
        # if getsize(f.stream) > max_size:
        #     flash('document size should be under 2M')
        #     return redirect(url_for('visitor.job'))

    if 'cv_en' in request.files:
        f = request.files['cv_en']
        path, ext = splitext(f.filename)
        f.filename = 'cv_en' + ext
        cv['en'] = f
    if 'cv_fr' in request.files:
        f = request.files['cv_fr']
        path, ext = splitext(f.filename)
        f.filename = 'cv_fr' + ext
        cv['fr'] = request.files['cv_fr']
    if 'cv_zh' in request.files:
        f = request.files['cv_zh']
        path, ext = splitext(f.filename)
        f.filename = 'cv_zh' + ext
        cv['zh'] = request.files['cv_zh']
    lm = request.files['lm']
    attachments = []
    for key, item in cv.items():
        attachments.append((item.filename, item.read()))
    attachments.append((lm.filename, lm.read()))
    message = mail.EmailMessage(sender='Admin of AFCP <lutianming1005@gmail.com>',
                   to='lutianming1005@hotmail.com')
    message.subject = 'New application sent by AFCP'
    message.attachments = attachments
    message.body = u"""
    Madame, Monsieur,

    Une nouvelle candidature pour le poste {0} a été envoyée par l'intermédiaire du site de l'AFCP, l'offre y étant publiée.

    Veuillez trouver ci-joint le CV et la lettre de motivation de {1} {2} pour cette candidature. Vous pouvez le joindre à l'adresse e-mail {3}

    Bien à vous,

    L'équipe AFCP
    """.format(job, first_name, last_name, email)
    message.send()
    flash('mail sent')
    return redirect(url_for('visitor.job'))
