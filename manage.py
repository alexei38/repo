#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.script import Manager, Server
from app import app, db
from app.models import *

manager = Manager(app)
runserver = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", runserver)

@manager.command
def create():
    db.create_all()
    fixtures()

@manager.command
def drop():
    db.drop_all()

def fixtures():
    db.session()
    repo_names = ['6.0.devel', '6.1.devel', '6.0.release', '6.1.release']
    for repo_name in repo_names:
        repo = Repo(repo_name, '/mnt/repo/%s' % repo_name, repo_name)
        db.session.add(repo)
        db.session.commit()

        snapshot = Snapshot(name=repo_name, type='current', path='/mnt/repo/meta/%s' % repo_name, filelist='', repo_id=repo.id)
        db.session.add(snapshot)
        db.session.commit()

if __name__ == "__main__":
    manager.run()