# -*- coding: utf-8 -*-

from app import app, db
from flask.views import MethodView
from flask import request, render_template, url_for, redirect, flash, send_from_directory
from werkzeug.utils import secure_filename
from forms import RepoForm, SnapshotForm, UploadForm
from models import Repo, Snapshot
from operator import itemgetter
import os, sys, time, json, uuid, shutil
from datetime import datetime

""" Форматируем дату в темплейтах """
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    return date.strftime('%d.%m.%Y %H:%M')

""" 404 page not found "route" """
@app.errorhandler(404)
def not_found(error):
    title = "404 Page not found"
    return render_template('404.html', title=title), 404

""" 500 server error "route" """
@app.errorhandler(500)
def server_error(error):
    title = "500 Server Error"
    db.session.rollback()
    return render_template('500.html', title=title), 500

""" Отдаем всем файлы как раньше """
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
            date_modify = os.path.getmtime(full_path)
            date_modify = datetime.fromtimestamp(date_modify)
            items.append(('..', parent_path, True, sizeof_fmt(os.path.getsize(full_path)), date_modify))
    for f in os.listdir(full_path):
        real_path = os.path.join(full_path, f)
        link_path = os.path.join('/', path, f)
        date_modify = os.path.getmtime(real_path)
        date_modify = datetime.fromtimestamp(date_modify)
        items.append((f, link_path, os.path.isdir(real_path), sizeof_fmt(os.path.getsize(real_path)), date_modify))
        items.sort(key=itemgetter(0))
        items.sort(key=itemgetter(2), reverse=True)

    return render_template('filelist.html', items=items)

""" Отдаем repo файлы из снапшота, остальные из репозитория """
@app.route('/snapshot/<snapshot>/<path:path>')
def get_snapshot_file(snapshot,path=''):
    snapshot = Snapshot.query.filter(Snapshot.name == snapshot).first()
    repo_path = os.path.join(snapshot.repo.path, path)
    if path.startswith('repodata'):
        full_path = os.path.join(snapshot.path, path)
    else:
        full_path = repo_path
    file = os.path.dirname(full_path)
    folder = os.path.basename(full_path)
    return send_from_directory(file, folder, as_attachment=True)

""" Загрузка файлов """
@app.route('/upload/', methods=['GET', 'POST'])
def upload_view():
    if request.method == 'GET':
        form = UploadForm()
        return render_template('upload.html', form=form)

    if request.method == 'POST':
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
                ret = "%s/snapshot/%s" % (app.config['SITE_URL'], snapshot.name)
            else:
                ret = "%s/%s" % (app.config['SITE_URL'], repo.name)
            generate_matadata(repo.path,repo.path)
            return ret

        if 'key' in request.form and request.form['key'] == app.config['REPO_KEY']:
            need_args = ['repo_name', 'key', 'arch']
            if len(set(request.form).intersection(need_args)) == len(set(need_args)) and request.files.getlist("file"):
                link = upload_files(request)
                return json.dumps({'data': 'ok', 'url': link})
            else:
                return json.dumps({'data': 'error', 'msg' : 'need mode args'})
        else:
            form = UploadForm()
            if form.validate_on_submit():
                link = upload_files(request)
                flash(u'Выполненно успешно!', 'success')
                if 'snapshot' in request.form:
                    flash(u'Создан snapshot %s' % link, 'success')
                return redirect(url_for('upload_view'))
            else:
                flash_errors(form)
            return render_template('upload.html', form=form)

""" Репозитории """
@app.route('/repo/', methods=['GET', 'POST'])
def repo_view():
    if request.method == 'GET':
    	repos = Repo.query.all()
        form = RepoForm()
        return render_template('repo.html', form=form, repos=repos)

    if request.method == 'POST':
        repos = Repo.query.all()
        form = RepoForm()
        if form.validate_on_submit():
            repo_path = os.path.join(app.config['BASE_PATH'], request.form['name'])
            repo = Repo(request.form['name'], repo_path, request.form['comment'])
            db.session()
            db.session.add(repo)
            db.session.commit()
            if not os.path.exists(repo_path):
                os.mkdir(repo_path)
            if 'snapshot' in request.form:
                check = Snapshot.query.filter(Snapshot.name == request.form['name'], 
                                              Snapshot.type == 'master',
                                              Snapshot.repo_id == repo.id).all()
                if check:
                    flash(u'Snapshot уже существует', 'error')
                else:
                    snapshot = Snapshot(  name=repo.name,
                                          type='master',
                                          path=repo.path,
                                          repo_id=repo.id
                                        )
                    db.session()
                    db.session.add(snapshot)
                    db.session.commit()
                    generate_matadata(repo.path, repo.path)
            flash(u'Выполненно успешно!', 'success')
            return redirect(url_for('repo_view'))
        flash_errors(form)
        return render_template('repo.html', form=form, repos=repos)

""" Снапшоты """
@app.route('/snapshot/', methods=['GET', 'POST'])
def view_snapshot():
    if request.method == 'GET':
        snapshots = Snapshot.query.all()
        form = SnapshotForm()
        return render_template('snapshot.html', form=form, snapshots=snapshots)

    if request.method == 'POST':
        snapshots = Snapshot.query.all()
        form = SnapshotForm()
        if form.validate_on_submit():
            repo = Repo.query.filter(Repo.id == request.form["repo_id"]).first()
            if request.form['type'] == 'test':
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
            return redirect(url_for('view_snapshot'))
        else:
            flash_errors(form)
        return render_template('snapshot.html', form=form, snapshots=snapshots)

""" Удаление снапшотов"""
@app.route('/snapshot/<name>', methods=['POST'])
def remove_snapshot(name):
    if request.method == 'POST':
        snapshot = Snapshot.query.filter(Snapshot.name == name, Snapshot.type == 'test').first()
        if snapshot:
            db.session()
            db.session.delete(snapshot)
            db.session.commit()
            shutil.rmtree(snapshot.path)
            flash(u'Выполненно успешно', 'success')
            return redirect(url_for('view_snapshot'))
        else:
            flash(u'Snapshot не найден', 'error')
            return redirect(url_for('view_snapshot'))

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
    genpkgmetadata.main(['-c', 'cache', '--output', meta_path, '-q', repo_path])

