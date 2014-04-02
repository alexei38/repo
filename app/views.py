# -*- coding: utf-8 -*-

from app import app, db
from flask.views import MethodView
from flask import Blueprint, request, render_template, url_for, redirect, flash
from forms import RepoForm
from models import *

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(unicode(error), 'error')

#frontend = Blueprint('frontend', __name__)
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

# general routes    
@app.route('/')
def index():
    return render_template('index.html')

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

app.add_url_rule('/repo/', view_func=RepoView.as_view('repo'))
