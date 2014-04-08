# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)
# Config
app.config.from_object('app.config.DevelopmentConfig')

# ProductionConfig
#app.config.from_object('repo.config.ProductionConfig')

import ldap
from flask.ext.login import LoginManager, UserMixin
def check_credentials(uid=None, name=None, passwd=None):
    try:
        ldap_client = ldap.initialize(app.config['LDAP_URI'])
        if name is not None and passwd is not None:
            ldap_client.simple_bind_s('uid=%s,%s' % (name, app.config['LDAP_BASE']), passwd)
    except:
        return None
    else:
    	if name is not None and passwd is not None:
    	    name = name 
    	else:
    	    name = uid
        ldap_filter = 'uid=%s' % name
        attrs = ['uidNumber', 'gidNumber', 'uid']
        ldap_res = ldap_client.search_s(app.config['LDAP_BASE'],ldap.SCOPE_SUBTREE, ldap_filter, attrs)
        if ldap_res:
            return ldap_res[0][1]
        else:
            return ldap_res

class User(UserMixin):
    def __init__(self, uid=None, name=None, passwd=None):
        ldap_res = check_credentials(uid=uid, name=name, passwd=passwd)
        self.active = False
        self.name = None
        self.id = None
        self.gid = None
        if ldap_res:
            self.active = True
            self.name = ldap_res['uid'][0]
            self.id = int(ldap_res['uidNumber'][0])
            self.gid = int(ldap_res['gidNumber'][0])

    def get_id(self):
        return self.name

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.active

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User(uid=userid)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app import models, views
