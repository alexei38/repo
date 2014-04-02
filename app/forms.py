from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, validators, ValidationError
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
