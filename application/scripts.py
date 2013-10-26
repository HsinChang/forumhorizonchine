#useful scripts to transform data
import lxml.html
from lxml.html.clean import Cleaner
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re

class CompanyDetails(object):
    """
    Properties: company email (email), minimal number of attachment (minattach), maximal number of attachment (maxattach).
    If no minattach is defined, it is set to resources.defaultAttachmentsNumber (2).
    If no maxattach is defined, it is set to minattach value.
    """
    def __init__(self, name, email, minattach=2, maxattach=None):
        self.name = name
        self.email    = email
        self.minattach   = minattach
        if maxattach is None:
            self.maxattach = minattach
        else:
            self.maxattach = maxattach

company_details = {
    'test':CompanyDetails('test','Antoine ORY-LAMBALLE <antoine.orylamballe@yahoo.fr>', 2, 4), # formulaire de test
    'huawei':CompanyDetails('huawei','recuit@huawei.com', 2, 4),     # Huawei - recrutement
    'huawei2':CompanyDetails('huawei',"ricky@huawei.com, francehr@huawei.com", 2, 4),
    'bmwbj':CompanyDetails('bmw', 'careerbj@bmw-brilliance.cn'),
    'bmwsy':CompanyDetails('bmw','careersy@bmw-brilliance.cn'),
    'tbsmarketing':CompanyDetails('tbsmarketing','Sallytbsdtv@gmail.com, kerong.cao@gmail.com'),
    'lyxorquant':CompanyDetails('lyxorquant','jean-charles.richard@lyxor.com'),
#      'bmwbj': CompanyDetails('antoine.orylamballe@yahoo.fr'),     # BMW - recrutement bj
#      'bmwsy': CompanyDetails('antoine.orylamballe@yahoo.fr'),     # BMW - recrutement sy
    'jpm':CompanyDetails('jpm','fei.shi@jpmchase.com'),     # Lyxor Asset Management - Quant R&D
    'michelin':CompanyDetails('michelin','assistant.recruiting@cn.michelin.com'),     # Michelin
}

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

def transform_enterprise():
    enterprises = ET.Element('enterprises')
    for company in company_details.itervalues():
        e = ET.Element('enterprise')
        e.set('name', company.name)
        e.set('shortname', company.name)

        emails = ET.SubElement(e, 'emails')
        email = ET.Element('email')
        email.text = company.email
        emails.append(email)

        enterprises.append(e)
        # e = EnterpriseModel.query(EnterpriseModel.name==company.name).get()
        # if e:
        #     #enterprise exist
        #     email = EmailModel.get(EmailModel.enterprise==e.key, EmailModel.email==company.email)
        #     if email:
        #         pass
        #     else:
        #         email = EmailModel(
        #             enterprise=e.key,
        #             email=company.email
        #         )
        # else:
        #     #create new enterprise
        #     e = EnterpriseModel(
        #         name = company.name,
        #         shortname = company.name
        #     )

        #     e.put()
        #     email = EmailModel(
        #         enterprise = e.key,
        #         email = company.email
        #     )
        #     email.put()
    output = prettify(enterprises)
    with open('enterprise.xml', 'w') as f:
        f.write(output)


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

        if len(job.forms) == 0:
            #apply online
            continue
        else:
            form = job.forms[0]
            id = form.fields['id']
            jobname = form.fields['jobname']
            company = form.fields['company']
            #transform to JobModel

            detail = company_details[id]
            enterprise = EnterpriseModel.query(EnterpriseModel.shortname==detail.name).get()
            j = JobModel.query(JobModel.en.title==title, job.enterprise==enterpise.key)
            if j:
                #job exist, pass
                continue

            email = EmailModel(EmailModel.enterpise==enterpise.key, EmailModel.email==detail.email)

            job = JobModel(
                type = jobtype,
                enterprise = enterpise.key,
                enterprise_mail = email.key,
                published = True,
                en = JobMetaModel(
                    published = True,
                    title = title,
                    content = content,
                ),
                default_lang = 'en',
                cv_required = ['en']
            )
            job.put()

transform_enterprise()
