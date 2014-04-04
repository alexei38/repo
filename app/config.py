# -*- coding: utf-8 -*-

import os

FLASK_APP_DIR = os.path.dirname(os.path.abspath(__file__))

class Config(object):
    CSRF_ENABLED = True
    SECRET_KEY = '\x07Y\x07\xcb\xc7\x1dy\x94\xbd\xd1\x85jD1\x89w(>m,w\xcd`\xa0'
    REPO_KEY = 'LsdDFjn234rF78hfuI234SDfe789fhw'
    BASE_PATH = '/mnt/repo'
    META_PATH = '/mnt/repo/meta'
    SITE_URL = 'http://repo.cc.naumen.ru'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(FLASK_APP_DIR, 'database.db')
    pass
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
class TestConfig(Config):
    DEBUG = False
    TESTING = True

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
