#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
import uuid, os, sys
from flask import Flask
from app import app, db
from app.models import Repo, Snapshot

migrate = Migrate(app, db)
manager = Manager(app)
runserver = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", runserver)
manager.add_command('db', MigrateCommand)

@manager.command
def create():
    """
    Usage ./manage.py db upgrade - to create database and migrate
    """
    #db.create_all()
    fixtures()

@manager.command
def drop():
    db.drop_all()

def fixtures():
    db.session()
    repo_names = ['6.0.devel', '6.1.devel', '6.0.release', '6.1.release']
    for repo_name in repo_names:
        repo_path = os.path.join(app.config['BASE_PATH'], repo_name)
        repo = Repo(name=repo_name, path=repo_path, comment=repo_name)
        db.session.add(repo)
        db.session.commit()
        snapshot = Snapshot(name=repo_name, type='master', path=repo_path, comment="text", repo_id=repo.id)
        db.session.add(snapshot)
        db.session.commit()
        generate_matadata(repo_path, repo_path)

def generate_matadata(repo_path, meta_path):
    repo_path = str(repo_path)
    meta_path = str(meta_path)
    sys.path.append('/usr/share/createrepo')
    if not os.path.exists(meta_path):
        os.mkdir(meta_path)
    if not os.path.exists(repo_path):
        os.mkdir(repo_path)
    import genpkgmetadata
    genpkgmetadata.main(['-c', 'cache', '--output', meta_path, '-q', repo_path])

if __name__ == "__main__":
    manager.run()