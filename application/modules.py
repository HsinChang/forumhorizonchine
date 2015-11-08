from flask import render_template, request
from models import JobModel, ActivityModel
from forms import ContactForm
from application import app, get_locale


def render_job():
    grouped_jobs = {}
    jobs = JobModel.query(JobModel.published == True,
                          JobModel.is_complete == True)

    for job in jobs:
        locale = get_locale()
        if job.meta[locale]["published"]:
            job.current_lang = locale
        else:
            job.current_lang = job.default_lang
            job.current = job.meta[job.current_lang]

        if job.enterprise in grouped_jobs:
            grouped_jobs[job.enterprise].append(job)
        else:
            grouped_jobs[job.enterprise] = [job]

    if len(grouped_jobs) == 0:
        grouped_jobs = None
    else:
        grouped_jobs = sorted(grouped_jobs.items(),
                              key=lambda i: i[0].get().order)
        for jobs in grouped_jobs:
            jobs[1].sort(key=lambda job: job.order)

    return render_template('module/job.html',
                           grouped_jobs=grouped_jobs,
                           languages=app.config['LANGUAGES'])


def render_activity():
    a = ActivityModel.query()
    return render_template('module/activities.html', activities=a)


def render_comment():
    form = ContactForm(request.form)
    return render_template('module/comment.html', form=form)


def render_banner(option=None):
    return render_template('module/banner.html')


MODULES = {
    'job': render_job,
    'activities': render_activity,
    'comment': render_comment,
    'banner': render_banner
}
