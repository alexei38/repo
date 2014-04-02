# -*- coding: utf-8 -*-

from app import db

class Repo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    path = db.Column(db.String(120), index = True, unique = True)
    comment = db.Column(db.Text(), index = False, unique = False)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    metadatas = db.relationship('Metadata', backref='repo',
                                lazy='dynamic')
    snapshots = db.relationship('Snapshot', backref='repo',
                                lazy='dynamic')

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
    repo_id = db.Column(db.Integer, db.ForeignKey('repo.id'), nullable=False, index=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    snapshots = db.relationship('Snapshot', backref='metadata',
                                lazy='dynamic')

    def __init__(self, name, path, repo_id):
        self.name = name
        self.path = path
        self.repo_id = repo_id

    def __repr__(self):
        return '<Metadata %r>' % (self.name)

class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    type = db.Column(db.String(64), index = False, unique = False)
    filelist = db.Column(db.Text(), index = False, unique = False)
    metadata_id = db.Column(db.Integer, db.ForeignKey('metadata.id'), nullable=False, index=True)
    repo_id = db.Column(db.Integer, db.ForeignKey('repo.id'), nullable=False, index=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __init__(self, name, type='current', filelist='', metadata_id=metadata_id, repo_id=repo_id):
        self.name = name
        self.type = type
        self.filelist = filelist
        self.metadata_id = metadata_id
        self.repo_id = repo_id

    def __repr__(self):
        return '<Snapshot %r>' % (self.name)