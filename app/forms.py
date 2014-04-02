# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SelectField, validators, ValidationError
from app.models import *
from app import db

class Unique(object):
    def __init__(self, model, field):
        self.model = model
        self.field = field

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError("%s already exists" % field.data)

class RepoForm(Form):
    name = TextField('name', [validators.Required(), Unique(Repo, Repo.name)])
    path = TextField('path', [validators.Required(), Unique(Repo, Repo.path)])
    comment = TextAreaField('comment')

class SnapshotForm(Form):
    name = TextField('name', [validators.Required(), Unique(Snapshot, Snapshot.name)])
    type = SelectField('type', choices=[('current', 'current'), ('test', 'test')])
    metadata_id = SelectField('metadata_id', choices=[(x.id, "%s - %s" % (x.name, x.path)) for x in Metadata.query.all()])
    repo_id = SelectField('repo_id', choices=[(x.id, "%s - %s" % (x.name, x.path)) for x in Repo.query.all()])

class MetadataForm(Form):
    name = TextField('name', [validators.Required(), Unique(Snapshot, Snapshot.name)])
    path = TextField('path', [validators.Required(), Unique(Repo, Repo.path)])
    repo_id = SelectField('repo_id', choices=[(x.id, "%s - %s" % (x.name, x.path)) for x in Repo.query.all()])
