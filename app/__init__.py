# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)

# Config
app.config.from_object('app.config.DevelopmentConfig')

# ProductionConfig
#app.config.from_object('repo.config.ProductionConfig')

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from app import models, views
