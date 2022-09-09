import os
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from odk_fieldmap.auth import login_required
from odk_fieldmap.db import get_db

bp = Blueprint('project', __name__)

@bp.route('/')
def index():
    db = get_db()
    projects = db.execute(
        'SELECT p.id, title, description, created, author_id, username'
        ' FROM project p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    if session['user_id']:
        tasks = get_tasks_for_user(session['user_id'])
        return render_template('project/index.html', tasks=tasks, projects=projects)
    return render_template('project/index.html', projects=projects)

import logging
from flask import current_app


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    current_app.logger.info("message")
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO project (title, description, author_id, base_dir)'
                ' VALUES (?, ?, ?, ?)',
                (title, description, g.user['id'], f'/example_files/{title}')
            )
            db.commit()

            # REMOVE LATER
            startingtask = int(request.form['startingtask'])
            lasttask = int(request.form['lasttask'])
            create_tasks(db, title, startingtask, lasttask)

            return redirect(url_for('project.index'))

    return render_template('project/create.html')

def create_tasks(db, title, first, last):
    # this has a bug if project name is the same
    project = db.execute(
        'SELECT id, title'
        ' FROM project WHERE title = ?',
        (title,)
    ).fetchone()

    error = None
    if not project:
        error = 'Project cannot be found.'
    if error is not None:
        flash(error)
        return

    task_numbers = range(first, last+1)
    for num in task_numbers:
        db.execute(
            'INSERT INTO task (task_number, project_id)'
            ' VALUES (?, ?)',
            (num, project['id'], )
        )
    db.commit()

def get_tasks_for_project(project_id):
    tasks = get_db().execute(
        'SELECT t.id, task_number, in_progress, last_selected, title'
        ' FROM task t JOIN project p ON t.[project_id] = p.id'
        ' WHERE t.[project_id] = ?',
        (project_id,)
    ).fetchall()
    return tasks

def get_in_progress_task_numbers(tasks):
    in_progress = []
    for task in tasks.values():
        if task['in_progress']:
            in_progress.append(task['task_number'])
    return in_progress

def get_tasks_for_user(user_id):
    tasks = get_db().execute(
        'SELECT t.id, task_number, project_id, last_selected, in_progress, title'
        ' FROM task t JOIN project p ON t.[project_id] = p.id'
        ' WHERE t.[task_doer] = ?',
        (user_id,)
    ).fetchall()
    return tasks

def get_project(id, check_author=True):
    project = get_db().execute(
        'SELECT p.id, title, description, created, author_id, username'
        ' FROM project p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if project is None:
        abort(404, f"Project id {id} doesn't exist.")

    if check_author and project['author_id'] != g.user['id']: abort(403)

    return project

# most recent attempt to download: https://gist.github.com/redlotus/3138bd661ceb02abf1f6
# def get_file_params(full_path, filename):
#     filepath = os.path.abspath(current_app.root_path)+"/../download/"+filename
#     if os.path.isfile(filepath):
#         return filename,"/download/"+filename,os.path.getsize(filepath)
#     with open(filepath, 'w') as outfile:
#         data = load_from_mongo("ddcss","queries",\
#             criteria = {"_id" : ObjectId(filename)}, projection = {'_id': 0})
#         #outfile.write(json.dumps(data[0], default=json_util.default))
#         outfile.write(dumps(data[0]))
#     return filename, "/download/"+filename, os.path.getsize(filepath)
#
# def download(file_id):
# 	(file_basename, server_path, file_size) = get_file_params(file_id)
# 	response = make_response()
# 	response.headers['Content-Description'] = 'File Transfer'
# 	response.headers['Cache-Control'] = 'no-cache'
# 	response.headers['Content-Type'] = 'application/octet-stream'
# 	response.headers['Content-Disposition'] = 'attachment; filename=%s' % file_basename
# 	response.headers['Content-Length'] = file_size
# 	response.headers['X-Accel-Redirect'] = server_path # nginx: http://wiki.nginx.org/NginxXSendfile
#
# 	return response

@bp.route('/<int:id>/map', methods=('GET', 'POST'))
def map(id):
    project = get_project(id, False)

    tasks = {}
    task_list = get_tasks_for_project(project['id'])
    for task in task_list:
        tasks[task['task_number']]=task

    msg = ""

    if request.method == 'POST':
        task_number = request.form['tasknum']
        error = None

        msg = "Attempted post with task number: "+task_number

        if not task_number:
            error = 'Task Number cannot be blank. Please select task again.'

            if error is not None:
                msg = error
                flash(error)
        else:
            db = get_db()
            matching_tasks = db.execute(
                'SELECT id, task_number FROM task'
                ' WHERE project_id = ? AND task_number = ?',
                (id, task_number)).fetchall()

            msg = matching_tasks

            db.execute(
                'UPDATE task SET in_progress = ?, task_doer = ?, last_selected = ?'
                ' WHERE project_id = ? AND task_number = ?',
                (1, session.get('user_id'), datetime.now(), id, task_number)
            )
            db.commit()

                # extra_actions = request.form.getlist('select_extras')
                # flash(extra_actions)
                # if extra_actions.contains('download'):
                #     new_filename = project['title']+"_task"+task_id+"_qrcode.gif"
                #     full_path = url_for('static', filename='example_files/Partial_Mikocheni/QR_codes/Mikocheni_buildings_198.gif')
                #     flash("Downloading: "+full_path)
                #     return send_from_directory(full_path, filename, as_attachment=True)
                # else:
                #     flash("No download requested.")
                # return redirect(url_for('project.index'))
    in_progress = get_in_progress_task_numbers(tasks)

    return render_template('project/map.html', project=project, tasks=tasks, in_progress=in_progress, msg=in_progress)



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    project = get_project(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE project SET title = ?, description = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('project.index'))

    return render_template('project/update.html', project=project)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_project(id)
    db = get_db()
    db.execute('DELETE FROM project WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('project.index'))
