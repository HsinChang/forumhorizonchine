from flask import Blueprint, render_template, abort, redirect, url_for
from models import JobModel
visitor = Blueprint('visitor', __name__)

#visitors
@visitor.route('/inscript')
def inscript():
    return render_template('inscription/forum2013.html')
#    return render_template('visitors/inscription.html')

@visitor.route('/program')
def program():
    return render_template('visitors/program.html')

@visitor.route('/exhibitors')
def exhibitors():
    return render_template('visitors/exhibitors.html')

@visitor.route('/job')
def job():
    jobs = JobModel.query()
    return render_template('visitors/job.html', jobs=jobs)

@visitor.route('/workpermit')
def workpermit():
    return render_template('visitors/workpermit.html')

@visitor.route('/')
def index():
    return redirect(url_for('visitor.program'))
