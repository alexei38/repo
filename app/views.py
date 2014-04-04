# -*- coding: utf-8 -*-

from app import app, db
from flask.views import MethodView
from flask import request, render_template, url_for, redirect, flash, send_from_directory
from werkzeug.utils import secure_filename
from forms import RepoForm, SnapshotForm, UploadForm
from models import Repo, Snapshot
from operator import itemgetter
import os, sys, time, json
from datetime import datetime

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    return date.strftime('%d.%m.%Y %H:%M')

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

@app.route('/snapshot/<snapshot>/<path:path>')
def get_snapshot(snapshot,path=''):
    snapshot = Snapshot.query.filter(Snapshot.name == snapshot).first()
    repo_path = os.path.join(snapshot.repo.path, path)
    if path.startswith('repodata'):
        full_path = os.path.join(snapshot.path, path)
    else:
        full_path = repo_path
    file = os.path.dirname(full_path)
    folder = os.path.basename(full_path)
    return send_from_directory(file, folder, as_attachment=True)

class UploadView(MethodView):
    def get(self):
        form = UploadForm()
        return render_template('upload.html', form=form)

    def post(self):
        def upload_files(request):
            files = request.files.getlist("file")
            repo = Repo.query.filter(Repo.name == request.form['repo_name']).first()
            folder = os.path.join(app.config['BASE_PATH'], repo.path, request.form['arch'])
            if not os.path.exists(folder):
                os.mkdir(folder)
            for file in files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder, filename))
            if 'snapshot' in request.form:
                import uuid
                name = str(uuid.uuid4())
                path = os.path.join(app.config['META_PATH'], name)
                db.session()
                snapshot = Snapshot( name=name,
                                     type='test',
                                     path=path,
                                     repo_id=repo.id
                                   )
                db.session.add(snapshot)
                db.session.commit()
                generate_matadata(repo.path, path)
                ret = "http://repo.cc.naumen.ru/snapshot/%s" % snapshot.name
            else:
                ret = "http://repo.cc.naumen.ru/%s" % repo.name
            return ret
            generate_matadata(repo.path,repo.path)

        if 'key' in request.form and request.form['key'] == app.config['REPO_KEY']:
            need_args = ['repo_name', 'key', 'arch']
            if len(set(request.form).intersection(need_args)) == len(set(need_args)) and request.files.getlist("file"):
                link = upload_files(request)
                return json.dumps({'data': 'ok', 'url': link})
            else:
                return json.dumps({'data': 'error', 'msg' : 'need mode args'})
        form = UploadForm()
        if form.validate_on_submit():
            upload_files(request)
            flash(u'Выполненно успешно!', 'success')
            return redirect(url_for('upload'))
        else:
            flash_errors(form)
        return render_template('upload.html', form=form)

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
            db.session.add(Repo(request.form['name'], os.path.join(app.config['BASE_PATH'], request.form['name']), request.form['comment']))
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
            repo = Repo.query.filter(Repo.id == request.form["repo_id"]).first()
            if request.form['type'] == 'test':
                import uuid
                name = str(uuid.uuid4())
                path = os.path.join(app.config['META_PATH'], name)
            else:
                name = repo.name
                path = repo.path
                check = Snapshot.query.filter(Snapshot.name == name, Snapshot.path == path, Snapshot.repo_id == repo.id).all()
                if check:
                    flash(u'Запись уже существует', 'error')
                    flash_errors(form)
                    return render_template('snapshot.html', form=form, snapshots=snapshots)
            db.session()
            db.session.add(Snapshot( name=name,
                                     type=request.form['type'],
                                     path=path,
                                     repo_id=request.form["repo_id"]
                                   )
                          )
            db.session.commit()
            generate_matadata(repo.path,path)
            flash(u'Выполненно успешно!', 'success')
            return redirect(url_for('snapshot'))
        else:
            flash_errors(form)
        return render_template('snapshot.html', form=form, snapshots=snapshots)

app.add_url_rule('/repo/', view_func=RepoView.as_view('repo'))
app.add_url_rule('/snapshot/', view_func=SnapshotView.as_view('snapshot'))
app.add_url_rule('/upload/', view_func=UploadView.as_view('upload'))


"""
  Helper functions
"""
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

def generate_matadata(repo_path, meta_path):
    sys.path.append('/usr/share/createrepo')
    import genpkgmetadata
    repo_path = str(repo_path)
    meta_path = str(meta_path)
    if not os.path.exists(meta_path):
        os.mkdir(meta_path)
    if not os.path.exists(repo_path):
        os.mkdir(repo_path)
    genpkgmetadata.main(['--output', meta_path, '-q', repo_path])

