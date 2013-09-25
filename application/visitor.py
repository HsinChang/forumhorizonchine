from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import JobModel, EnterpriseModel
from flask_mail import Message
from application import app
from google.appengine.api import mail

visitor = Blueprint('visitor', __name__)

#visitors
@visitor.route('/inscription')
def inscription():
    return render_template('visitors/inscription.html')
#    return render_template('visitors/inscription.html')

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
    jobname = request.form['jobname']
    enterprise = request.form['enterprise']
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    cv = request.files['cv']
    lm = request.files['lm']
    mail.send_mail('lutianming1005@gmail.com', 'lutianming1005@hotmail.com', subject='apply '+jobname,
                   body='test ' + first_name + ' ' + last_name, attachments=[('cv', cv.read()), ('lm', lm.read())])
    flash('mail sent')
    return redirect(url_for('visitor.job'))
