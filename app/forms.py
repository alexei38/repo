# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SelectField, validators, ValidationError, FileField, FieldList
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Repo, Snapshot
from app import app, db

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
    comment = TextAreaField('comment')

class SnapshotForm(Form):
    type = SelectField('type', choices=[('test', 'test'), ('master', 'master')])
    repo_id = QuerySelectField(query_factory=Repo.query.all,
                            get_pk=lambda a: a.id,
                            get_label=lambda a: "%s - %s" % (a.name, a.path))

class UploadForm(Form):
    file = FileField('file[]', [validators.Required()])
    repo_name = QuerySelectField(query_factory=Repo.query.all,
                            get_pk=lambda a: a.name,
                            get_label=lambda a: "%s - %s" % (a.name, a.path))
    arch = SelectField('type', choices=[('contrib', 'contrib'), ('i386', 'i386'), ('x86_64', 'x86_64'), ('noarch', 'noarch')])