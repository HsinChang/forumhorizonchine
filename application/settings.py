"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module,
           which should be kept out of version control.

"""

import os

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY

class Config(object):
    # Set secret keys for CSRF protection
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY
    # Flask-Cache settings
    CACHE_TYPE = 'gaememcached'

    LANGUAGES = {'en': _('English'), 'fr': _('French'), 'zh': _('Chinese')}

    #EMAILS
    CONTACT = ['ZHU Qi <realzhq@gmail.com>', 'LI Zheng <zheng.li@polytechnique.edu>', 'ZHANG Nan <nan.zhann@gmail.com>', 'DENG Ken <dengken524@live.cn>', 'Antoine ORY-LAMBALLE <antoine.orylamballe@yahoo.fr>', 'ZHU Tong <zhutong0114@gmail.com>']
    CC = ['ZHU Qi <realzhq@gmail.com>', 'LI Zheng <zheng.li@polytechnique.edu>', 'ZHANG Nan <nan.zhann@gmail.com>', 'DENG Ken <dengken524@live.cn>', 'Antoine ORY-LAMBALLE <antoine.orylamballe@yahoo.fr>', 'ZHU Tong <zhutong0114@gmail.com>']
    SENDER = 'Forum Horizon Chine <admin@forumhorizonchine.com>'


    #upload file size limit
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class Development(Config):
    DEBUG = True
    # Flask-DebugToolbar settings
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CSRF_ENABLED = True

class Testing(Config):
    TESTING = True
    DEBUG = True
    CSRF_ENABLED = True

class Production(Config):
    DEBUG = False
    CSRF_ENABLED = True
