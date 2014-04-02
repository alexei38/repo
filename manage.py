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
    db.session.add(Repo('6.0.devel', '/mnt/repo/6.0.devel', '6.0.devel'))
    db.session.add(Repo('6.0.release', '/mnt/repo/6.0.release', '6.0.release'))
    db.session.add(Repo('6.1.devel', '/mnt/repo/6.1.devel', '6.1.devel'))
    db.session.add(Repo('6.1.release', '/mnt/repo/6.1.release', '6.1.release'))
    db.session.commit()

if __name__ == "__main__":
    manager.run()