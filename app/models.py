# -*- coding: utf-8 -*-

from app import db

class Repo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    path = db.Column(db.String(120), index = True, unique = True)
    comment = db.Column(db.Text(), index = False, unique = False)

    def __init__(self, name, path, comment):
        self.name = name
        self.path = path
        self.comment = comment

    def __repr__(self):
        return '<Repo %r>' % (self.name)

class Metadata(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    path = db.Column(db.String(120), index = True, unique = True)
    repo_id = db.Column(db.Integer, db.ForeignKey('repo.id'))

    def __repr__(self):
        return '<Metadata %r>' % (self.name)

class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    filelist = db.Column(db.Text(), index = False, unique = False)
    metadata_id = db.Column(db.Integer, db.ForeignKey('metadata.id'))
    repo_id = db.Column(db.Integer, db.ForeignKey('repo.id'))

    def __repr__(self):
        return '<Snapshot %r>' % (self.name)