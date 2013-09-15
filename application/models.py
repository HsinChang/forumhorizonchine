"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb

ROLES ={'EXHIBITOR':'exhibitor', 'ADMIN': 'admin'}
OFFRE_TYPES = {'JOB': 'job', 'INTERN': 'internship'}

class JobModel(ndb.Model):
    title = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    poster = ndb.KeyProperty()
    date = ndb.DateProperty(auto_now_add=True)
    enterprise = ndb.KeyProperty(required=True)
    enterprise_mail = ndb.KeyProperty(required=True)
    content = ndb.TextProperty(required=True)


class EnterpriseModel(ndb.Model):
    name = ndb.StringProperty(required=True)
    shortname = ndb.StringProperty(required=True)


class EmailModel(ndb.Model):
    """
    email for enterprise
    """
    enterprise = ndb.KeyProperty(required=True)
    email = ndb.StringProperty(required=True)


class UserModel(ndb.Model):
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    role = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.key.id())
