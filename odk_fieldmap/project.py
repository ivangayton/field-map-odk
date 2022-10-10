import json
import logging
import os
import posixpath
import zipfile
from datetime import datetime

from flask import (Blueprint, current_app, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.exceptions import abort

from odk_fieldmap.auth import login_required
from odk_fieldmap.models import Project, Task, User, db

bp = Blueprint("project", __name__)

grid_filename = "grid.geojson"


@bp.route("/")
def index():
    projects = Project.query.join(User, Project.author_id == User.id).order_by(
        Project.created
    )

    if session.get("user_id"):
        tasks = get_tasks_for_user(session["user_id"])
        return render_template("project/index.html", tasks=tasks, projects=projects)
    return render_template("project/index.html", projects=projects)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    current_app.logger.info("message")
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        error = None

        if not title:
            error = "Title is required."
        else:
            # TODO: check theres not a project with this title already
            pass

        error = save_project_file(request, "files")

        if error is not None:
            flash(error)

        else:
            # try:
            user_id = g.user["id"]
            project = Project(
                title=title,
                description=description,
                author_id=user_id,
                # TODO get rid of this in db
                base_dir=get_relative_project_path(title),
            )
            db.session.add(project)
            db.session.commit()

            create_tasks(title)
            # except:
            #     rollback_project_creation(title, error)
            #     flash('Project creation failed.')

            return redirect(url_for("project.index"))

    return render_template("project/create.html")


def get_project_folder(title):
    static_folder_path = current_app.config["STATIC_FOLDER"]
    upload_folder_name = current_app.config["PROJECTS_UPLOAD_FOLDER_NAME"]
    return os.path.join(static_folder_path, upload_folder_name, title)


def get_relative_project_path(title):
    upload_folder_name = current_app.config["PROJECTS_UPLOAD_FOLDER_NAME"]
    return posixpath.join(upload_folder_name, title)


def save_project_file(request, form_field_name):
    if form_field_name not in request.files:
        return "No file part"
    current_app.logger.info(request.files)
    upload_files = request.files.getlist(form_field_name)
    current_app.logger.info(upload_files)
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if not upload_files:
        return "No selected file"
    elif len(upload_files) > 1:
        return "Expecting 1 file"

    file = upload_files[0]
    full_path = get_project_folder(request.form["title"])
    if not os.path.isdir(full_path):
        os.makedirs(full_path)
    else:
        return "A project directory with this name already exists"

    file_like_object = file.stream._file
    zipfile_ob = zipfile.ZipFile(file_like_object)
    zipfile_ob.extractall(full_path)
    zipfile_ob.close()

    flash("Upload succeeded")
    return None


def get_task_ids_from_geojson(title):
    # import ipdb; ipdb.set_trace()
    project_path = get_project_folder(request.form["title"])
    full_path = os.path.join(project_path, grid_filename)

    file = open(full_path)
    data = json.load(file)

    task_ids = []
    for feature in data["features"]:
        task_ids.append(feature["properties"]["id"])
    return task_ids


def create_tasks(title):
    project = db.session.query(Project).where(Project.title == title).first()

    error = None
    if not project:
        raise ValueError("Project cannot be found.")

    task_ids = get_task_ids_from_geojson(title)
    for num in task_ids:
        task = Task(feature_id=num, project_id=project["id"])
        db.session.add(task)
    db.session.commit()


def rollback_project_creation(title, error):
    # delete project
    # project = db.session.query(Project).where(Project.title == title).first()
    # db.session.delete(project)

    # # delete tasks
    # tasks = db.session.query(Task).where(Task.project_id == project.id)
    # for task in tasks:
    #     db.session.delete(task)

    # delete folder
    pass


def get_tasks_for_project(project_id):
    tasks = (
        db.session.query(Task)
        .join(Project, Task.project_id == Project.id)
        .where(Project.id == project_id)
    )

    return tasks


def get_tasks_for_user(user_id):
    tasks = (
        db.session.query(Task)
        .join(Project, Task.project_id == Project.id)
        .where(Task.task_doer == user_id)
    )
    return tasks


def get_project(id, check_author=True):
    project = (
        db.session.query(Project)
        .join(User, Project.author_id == User.id)
        .where(Project.id == id)
        .first()
    )

    if project is None:
        abort(404, f"Project id {id} doesn't exist.")

    if check_author and project["author_id"] != g.user["id"]:
        abort(403)

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

# todo: make this work
def check_for_feature_id(request):
    feature_id = request.form["tasknum"]
    error = None

    msg = "Attempted post with task number: " + feature_id

    if not feature_id:
        error = "Task Number cannot be blank. Please select task again."

        if error is not None:
            msg = error
            flash(error)
    return feature_id


@bp.route("/<int:id>/map", methods=("GET", "POST"))
def map(id):
    project = get_project(id, False)

    task_list = get_tasks_for_project(project["id"])
    tasks = task_by_feature_id(task_list)

    if request.method == "POST":
        if session.get("user_id"):

            feature_id = check_for_feature_id(request)
            if feature_id:
                matching_tasks = db.session.query(Task).where(
                    Task.project_id == id, Task.feature_id == feature_id
                )
                msg = matching_tasks

                # TODO fix this w/ postgres query
                # db.execute(
                #     'UPDATE task SET status = ?, task_doer = ?, last_selected = ?'
                #     ' WHERE project_id = ? AND feature_id = ?',
                #     (1, session.get('user_id'), datetime.now(), id, feature_id)
                # )
                # db.session.commit()

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

            path = get_relative_project_path(project["title"])
            return render_template(
                "project/map.html", project=project, project_path=path, tasks=tasks
            )
        else:
            return redirect(url_for("auth.login"))
    else:
        path = get_relative_project_path(project["title"])
        return render_template(
            "project/map.html", project=project, project_path=path, tasks=tasks
        )


def task_by_feature_id(tasks):
    task_dict = {}
    for task in tasks:
        task_dict[task["feature_id"]] = task
    return task_dict


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    project = get_project(id)

    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["description"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            project = db.session.query(Project).where(Project.id == id).first()
            project.title = title
            project.description = desc
            db.session.commit()

            return redirect(url_for("project.index"))

    return render_template("project/update.html", project=project)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_project(id)
    project = db.session.query(Project).where(Project.id == id).first()
    db.session.delete(project)
    db.session.commit()

    return redirect(url_for("project.index"))


@bp.route("/<int:id>/release", methods=("POST",))
@login_required
def release(proj_id, feature_id):
    feature_id = check_for_feature_id(request)

    if feature_id is None:
        abort(404, f"Task number is required.")

    task = check_task_doer(proj_id, feature_id)
    task = db.session.query(Task).where(Task.id == id).first()
    db.session.delete(task)
    db.commit()

    return redirect(url_for("project.index"))


def check_task_doer(proj_id, feature_id):
    task = (
        db.session.query(Task)
        .where(Task.project_id == proj_id, Task.feature_id == feature_id)
        .first()
    )

    if task is None:
        abort(404, f"Project id {id} doesn't exist.")

    if check_author and task["task_doer"] != g.user["id"]:
        abort(403)

    return task
