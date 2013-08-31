"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb

OFFRE_TYPES = {'JOB': 'job', 'INTERN': 'internship'}

class JobModel(ndb.Model):
    title = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    poster = ndb.KeyProperty(required=True)
    date = ndb.DateProperty(auto_now_add=True)
    content = ndb.TextProperty()


class ExhibitorModel(ndb.Model):
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    entreprise = ndb.StringProperty(required=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.key.id())
