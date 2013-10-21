import lxml.html
from lxml.html.clean import Cleaner
import re
#from models import JobModel

def import_jobs(filename):
    html = lxml.html.parse(filename)
    cleaner = Cleaner(comments=True)
    html = cleaner.clean_html(html)
    jobs = html.xpath('//div[@class="block-job"]')

    for job in jobs[1:]:
        jobtype = job.find('.//div[@class="right"]')
        title = job.find('.//div[@class="apply-button"]/h3')

        content = job.xpath('./div')[1]
        content = lxml.html.tostring(content)

        m = re.search('<\w+ class="apply-button"', content)
        content = content[5:m.start()]

        if len(job.forms) > 0:
            form = job.forms[0]
            id = form.fields['id']
            jobname = form.fields['jobname']
            company = form.fields['company']

        #transform to JobModel

import_jobs('templates/visitors/job.html')
