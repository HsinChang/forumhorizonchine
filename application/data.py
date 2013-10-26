import xml.etree.ElementTree as ET
from models import EnterpriseModel, JobModel, EmailModel
from os.path import splitext
from flask import flash

def import_enterprise(f):
    path, ext = splitext(f.filename)
    if ext != '.xml':
        #not xml file
        flash('not xml file')
        return -1
    content = f.read()
    root = ET.fromstring(content)
    for e in root.iter('enterprise'):
        name = e.get('name')
        shortname = e.get('shortname')
        model = EnterpriseModel.query(EnterpriseModel.name==name).get()
        if not model:
            model = EnterpriseModel(
                name = name,
                shortname = shortname
            )
            model.put()

        emails = e.find('emails')
        for email in emails.iter('email'):
            if not email.text or len(email.text) == 0:
                continue

            mail = EmailModel.query(EmailModel.enterprise==model.key, EmailModel.email==email.text).get()
            if not mail:
                mail = EmailModel(
                    enterprise = model.key,
                    email = email.text
                )
                mail.put()
    flash('import success!')
    return 0

def export_enterprise():
    enterprises = EnterpriseModel().query()
    root = ET.Element('enterprises')
    for enterprise in enterprises:
        e = ET.Element('enterprise')
        e.set('name', enterprise.name)
        e.set('shortname', enterprise.shortname)
        root.append(e)

        sub = ET.SubElement(e, 'emails')
        emails = EmailModel.query(EmailModel.enterprise==enterprise.key)

        for email in emails:
            element = ET.Element('email')
            element.text = email.email
            sub.append(element)

    return ET.tostring(root)
