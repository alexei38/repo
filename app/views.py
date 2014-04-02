# -*- coding: utf-8 -*-

from app import app, db
from flask.views import MethodView
from flask import request, render_template, url_for, redirect, flash, send_from_directory
from forms import RepoForm, SnapshotForm
from models import *
from operator import itemgetter
import os

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(unicode(error), 'error')

def sizeof_fmt(num):
    for x in ['B','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

# 404 page not found "route"
@app.errorhandler(404)
def not_found(error):
    title = "404 Page not found"
    return render_template('404.html', title=title), 404

# 500 server error "route"
@app.errorhandler(500)
def server_error(error):
    title = "500 Server Error"
    db.session.rollback()
    return render_template('500.html', title=title), 500

# Отдаем всем файлы как раньше
@app.route('/')
@app.route('/<path:path>')
def file_list(path=''):
    base_path = app.config['BASE_PATH']
    full_path = os.path.join(base_path, path)
    print base_path
    if not os.path.isdir(full_path):
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path), as_attachment=True)
    items = []

    if path not in ['', '/']:
        parent_path = os.path.normpath(os.path.join('/', path, '..'))
        if parent_path != '.':
            items.append(('..', parent_path, True, 0))
    for f in os.listdir(full_path):
        real_path = os.path.join(full_path, f)
        link_path = os.path.join('/', path, f)
        items.append((f, link_path, os.path.isdir(real_path), sizeof_fmt(os.path.getsize(real_path))))
        items.sort(key=itemgetter(0))
        items.sort(key=itemgetter(2), reverse=True)

    return render_template('filelist.html', items=items)

class RepoView(MethodView):
    def get(self):
    	repos = Repo.query.all()
        form = RepoForm()
        return render_template('repo.html', form=form, repos=repos)

    def post(self):
        repos = Repo.query.all()
        form = RepoForm()
        if form.validate_on_submit():
            db.session()
            db.session.add(Repo(request.form['name'], request.form['path'], request.form['comment']))
            db.session.commit()
            flash(u'Выполненно успешно!', 'success')
            return redirect(url_for('repo'))
        else:
            flash_errors(form)
        return render_template('repo.html', form=form, repos=repos)

class SnapshotView(MethodView):
    def get(self):
        snapshots = Snapshot.query.all()
        form = SnapshotForm()
        return render_template('snapshot.html', form=form, snapshots=snapshots)

    def post(self):
        snapshots = Snapshot.query.all()
        form = SnapshotForm()
        if form.validate_on_submit():
            #db.session()
            #db.session.add(Repo(request.form['name'], request.form['path'], request.form['comment']))
            #db.session.commit()
            flash(u'Выполненно успешно!', 'success')
            return redirect(url_for('snapshot'))
        return render_template('snapshot.html', form=form, snapshots=snapshots)

app.add_url_rule('/repo/', view_func=RepoView.as_view('repo'))
app.add_url_rule('/snapshot/', view_func=SnapshotView.as_view('snapshot'))
