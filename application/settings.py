"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module,
           which should be kept out of version control.

"""

import os

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY


DEBUG_MODE = False

# Auto-set debug mode based on App Engine dev environ
if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    DEBUG_MODE = True

DEBUG = DEBUG_MODE

# Set secret keys for CSRF protection
SECRET_KEY = CSRF_SECRET_KEY
CSRF_SESSION_KEY = SESSION_KEY

CSRF_ENABLED = True

# Flask-DebugToolbar settings
DEBUG_TB_PROFILER_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False


# Flask-Cache settings
CACHE_TYPE = 'gaememcached'

LANGUAGES = {'en': ('English'), 'fr': ('French'), 'zh': ('Chinese')}

#EMAILS
CONTACT = ['ZHANG Nan <nan.zhann@gmail.com>',
           'ZHU Tong <zhutong0114@gmail.com>',
           'CHEN Cheng <chchen81@gmail.com>',
           'Tianming LU <lutianming1005@gmail.com>']
CC = ['ZHU Tong <zhutong0114@gmail.com>',
      'CHEN Cheng <chchen81@gmail.com>',
      'Tianming LU <lutianming1005@gmail.com>']
SENDER = 'Forum Horizon Chine <admin@forumhorizonchine.com>'
ADMINS = [
    'tank2885360@gmail.com',
    'xuanlin.9211@gmail.com',
    'zijiaoli.julie@gmail.com',       
    'realzhq@gmail.com',
    'gaorunning@gmail.com',
    'lutianming1005@gmail.com',
    'beyondhyx@gmail.com',
    'heyw0216@gmail.com',
    'weiwenjia121@gmail.com',
    'zhutong0114@gmail.com',
    'chchen81@gmail.com',
    'xiangjunqian@gmail.com',
    'flyzhangyi@gmail.com',
    'u.philippart@gmail.com',
    'renheureux@gmail.com',
    'panwei.whu@gmail.com',
]

#upload file size limit
MAX_CONTENT_LENGTH = 1 * 1024 * 1024
BABEL_DEFAULT_LOCALE = 'fr'

class Config(object):
    # Set secret keys for CSRF protection
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY
    # Flask-Cache settings
    CACHE_TYPE = 'gaememcached'

    LANGUAGES = {'en': ('English'), 'fr': ('French'), 'zh': ('Chinese')}

    #EMAILS
    CONTACT = ['ZHANG Nan <nan.zhann@gmail.com>',
                'ZHU Tong <zhutong0114@gmail.com>',
               ]
    CC = ['ZHANG Nan <nan.zhann@gmail.com>',
          'ZHU Tong <zhutong0114@gmail.com>']
    SENDER = 'Forum Horizon Chine <admin@forumhorizonchine.com>'

    #upload file size limit
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024


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
