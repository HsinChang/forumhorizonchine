"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb

ROLES ={'EXHIBITOR':'exhibitor', 'ADMIN': 'admin'}
OFFRE_TYPES = {'JOB': 'job', 'INTERN': 'internship'}

class JobMetaModel(ndb.Model):
    published = ndb.BooleanProperty(required=True)
    title = ndb.StringProperty()
    content = ndb.TextProperty()

class JobModel(ndb.Model):
    type = ndb.StringProperty(required=True)
    poster = ndb.KeyProperty()
    date = ndb.DateProperty(auto_now_add=True)
    is_complete = ndb.BooleanProperty(default=True)
    is_online = ndb.BooleanProperty(required=True)
    apply_url = ndb.StringProperty()
    enterprise = ndb.KeyProperty()
    enterprise_mail = ndb.KeyProperty()

    published = ndb.BooleanProperty(required=True)
    fr = ndb.StructuredProperty(JobMetaModel)
    en = ndb.StructuredProperty(JobMetaModel)
    zh = ndb.StructuredProperty(JobMetaModel)
    default_lang = ndb.StringProperty(required=True)
    cv_required = ndb.StringProperty(repeated=True)


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
