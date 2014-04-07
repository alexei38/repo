# -*- coding: utf-8 -*-

from app import db
import datetime

class Repo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    path = db.Column(db.String(120), index = True, unique = True)
    comment = db.Column(db.Text(), index = False, unique = False)
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)
    updated_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    snapshots = db.relationship('Snapshot', backref='repo',
                                lazy='dynamic')

    def __init__(self, name, path, comment):
        self.name = name
        self.path = path
        self.comment = comment

    def __repr__(self):
        return '<Repo %r>' % (self.name)

class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    path = db.Column(db.String(120), index = True, unique = True)
    type = db.Column(db.String(64), index = False, unique = False)
    comment = db.Column(db.Text(), index = False, unique = False)
    repo_id = db.Column(db.Integer, db.ForeignKey('repo.id'), nullable=False, index=True)
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)

    def __init__(self, name, type='current', path='', comment='', repo_id=repo_id):
        self.name = name
        self.type = type
        self.comment = comment
        self.path = path
        self.repo_id = repo_id

    def __repr__(self):
        return '<Snapshot %r>' % (self.name)