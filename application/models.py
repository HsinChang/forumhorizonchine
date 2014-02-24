"""
models.py

App Engine datastore models

"""

from google.appengine.ext import ndb
from gettext import gettext


ROLES = {'EXHIBITOR':'exhibitor', 'ADMIN': 'admin'}
OFFRE_TYPES = {'JOB': gettext('Job'), 'INTERN': gettext('Internship')}


class JobMetaModel(ndb.Model):
    published = ndb.BooleanProperty(required=True)
    title = ndb.StringProperty()
    content = ndb.TextProperty()


class JobModel(ndb.Model):
    type = ndb.StringProperty(required=True)
    order = ndb.IntegerProperty(default=0)
    poster = ndb.KeyProperty()
    date = ndb.DateProperty(auto_now_add=True)
    is_complete = ndb.BooleanProperty(default=True)
    is_online = ndb.BooleanProperty(required=True)
    apply_url = ndb.StringProperty()
    enterprise = ndb.KeyProperty()
    enterprise_email = ndb.KeyProperty()

    published = ndb.BooleanProperty(required=True)
    meta = ndb.JsonProperty()
    # fr = ndb.StructuredProperty(JobMetaModel)
    # en = ndb.StructuredProperty(JobMetaModel)
    # zh = ndb.StructuredProperty(JobMetaModel)
    default_lang = ndb.StringProperty(required=True)
    cv_required = ndb.StringProperty(repeated=True)


class EnterpriseModel(ndb.Model):
    name = ndb.StringProperty(required=True)
    shortname = ndb.StringProperty(required=True)
    order = ndb.IntegerProperty(default=0)


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


class ForumModel(ndb.Model):
    date = ndb.DateProperty(required=True)
    address = ndb.StringProperty(required=True)
    duration = ndb.IntegerProperty()
    registrable = ndb.BooleanProperty(required=True)
    register_link = ndb.StringProperty()


class ActivityModel(ndb.Model):
    meta = ndb.JsonProperty()
    date = ndb.DateProperty(required=True)
    address = ndb.StringProperty(required=True)
    registrable = ndb.BooleanProperty(required=True)
    register_link = ndb.StringProperty()


class PageModel(ndb.Model):
    meta = ndb.JsonProperty()
    url = ndb.StringProperty()


MENU_TYPE = ['TOP', 'SIDE_NAV', 'SIDE_ENTRY']


class MenuModel(ndb.Model):
    id = ndb.StringProperty(required=True)
    meta = ndb.JsonProperty()
    parent = ndb.KeyProperty()
    order = ndb.IntegerProperty()
    type = ndb.StringProperty()
    children = ndb.KeyProperty(repeated=True)
    action = ndb.StringProperty()
