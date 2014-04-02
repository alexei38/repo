# -*- coding: utf-8 -*-

import os

FLASK_APP_DIR = os.path.dirname(os.path.abspath(__file__))

class Config(object):
    CSRF_ENABLED = True
    SECRET_KEY = 'you-will-never-guess'
    pass
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(FLASK_APP_DIR, 'production.db')

class TestConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(FLASK_APP_DIR, 'test.db')

class DevelopmentConfig(Config):
    '''Use "if app.debug" anywhere in your code, that code will run in development code.'''
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(FLASK_APP_DIR, 'development.db')
    BASE_PATH = os.path.dirname(FLASK_APP_DIR)