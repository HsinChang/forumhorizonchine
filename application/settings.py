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
CONTACT = ['ZHU Qi <realzhq@gmail.com>', 'ZHANG Nan <nan.zhann@gmail.com>',
           'DENG Ken <dengken524@live.cn>', 'ZHU Tong <zhutong0114@gmail.com>',
           'Antoine ORY-LAMBALLE <antoine.orylamballe@yahoo.fr>',
           'Tianming LU <lutianming1005@gmail.com>']
CC = ['ZHU Qi <realzhq@gmail.com>', 'ZHANG Nan <nan.zhann@gmail.com>',
      'DENG Ken <dengken524@live.cn>', 'ZHU Tong <zhutong0114@gmail.com>',
      'Antoine ORY-LAMBALLE <antoine.orylamballe@yahoo.fr>',
      'Tianming LU <lutianming1005@gmail.com>']
SENDER = 'Forum Horizon Chine <admin@forumhorizonchine.com>'
ADMINS = [
    'nan.zhann@gmail.com',
    'realzhq@gmail.com',
    'guan.pengpourss@gmail.com',
    'gaorunning@gmail.com',
    'dengken524@live.cn',
    'lutianming1005@gmail.com',
    'beyondhyx@gmail.com',
    'liuyx11241@gmail.com',
    'heyw0216@gmail.com',
    'weiwenjia121@gmail.com',
    'zhutong0114@gmail.com',
    'chchen81@gmail.com',
    'julien.legrand@mines-paristech.fr',
    'xiangjunqian@gmail.com',
    'laurent.erx@gmail.com',
    'flyzhangyi@gmail.com',
    'u.philippart@gmail.com',
    'zengzhizhou@gmail.com'
]

#upload file size limit
MAX_CONTENT_LENGTH = 1 * 1024 * 1024


class Config(object):
    # Set secret keys for CSRF protection
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY
    # Flask-Cache settings
    CACHE_TYPE = 'gaememcached'

    LANGUAGES = {'en': ('English'), 'fr': ('French'), 'zh': ('Chinese')}

    #EMAILS
    CONTACT = ['ZHU Qi <realzhq@gmail.com>', 'ZHANG Nan <nan.zhann@gmail.com>',
               'DENG Ken <dengken524@live.cn>', 'ZHU Tong <zhutong0114@gmail.com>',
               'Antoine ORY-LAMBALLE <antoine.orylamballe@yahoo.fr>']
    CC = ['ZHU Qi <realzhq@gmail.com>', 'ZHANG Nan <nan.zhann@gmail.com>',
          'DENG Ken <dengken524@live.cn>', 'ZHU Tong <zhutong0114@gmail.com>',
          'Antoine ORY-LAMBALLE <antoine.orylamballe@yahoo.fr>']
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
