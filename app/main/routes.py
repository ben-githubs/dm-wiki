from datetime import datetime
from os import environ
from flask_login import login_required, current_user
import requests
import re

from flask import abort, Blueprint, json, flash, render_template, redirect, request, session, url_for
from flask import current_app as app
from markdown import markdown
from sqlalchemy import func, desc

from .model_help import create_page, get_page_by_abs_path, get_path_from_id, get_project_by_title, get_project_tree, get_projects_by_owner, url_to_title

from . import forms
from . import models as m
from .models import db
from .auth import User
from .paths import Path
from .. import lm

ority_url = 'http://localhost:5001/'

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder = 'templates',
    static_folder = 'static'
)

@lm.user_loader
def load_user(id):
    print(id)
    url = r'http://localhost:5001/api/v1/user/get'
    data = {'id': id}
    headers = {'API-Key': environ.get('ORITY_API_KEY')}
    r = requests.post(url, headers=headers, json=data)
    if r.status_code == requests.codes.ok:
        user = User(**json.loads(r.content))
        return user
    return None

@main_bp.route("/", methods=['GET'])
def index():
    if current_user.is_authenticated:
        projects = get_projects_by_owner(current_user.id)
        return render_template('index.html',
            title = "DM Wiki",
            projects = projects
        )
    return render_template('front_page.html', title='DM Wiki')

@main_bp.route("/search", methods=['POST'])
def search():
    term = request.form.get('search_bar')
    # -- DO NOT TOUCH WITHOUT LOTS OF THOUGHT -- #
    query = m.Page.query.filter(m.Page.__ts_vector__.match(term))
    query = query.order_by(desc(func.ts_rank_cd(m.Page.__ts_vector__, term)))
    results = query.all()
    # ------------------------------------------ #
    print(results)
    return render_template('search_results.html',
        title = 'Search Results',
        search_term = term,
        results = results
    )

@login_required
@main_bp.route('/new/project', methods=['POST', 'GET'])
def new_project():
    """ Create a new project to house our articles. """
    form = forms.Project()
    if form.validate_on_submit():
        # Make sure the name isn't taken
        uid = current_user.id
        if get_project_by_title(uid, form.title.data):
            form.title.errors = ['You already have a project with this title. Please choose again.']
            print('Form error: name already in use.')
        else:
            # Create page first, because we have to link it to the Project
            page = m.Page(
                title = form.title.data,
                public = form.public.data,
                text = form.text.data,
                owner_id = uid
            )
            db.session.add(page)
            db.session.commit()
            # Now create project
            project = m.Project(
                title = form.title.data,
                public = form.public.data,
                owner_id = uid,
                page_id = page.id
            )
            db.session.add(project)
            db.session.commit()
            title = form.title.data.replace(' ', '_')
            redirect(url_for('main_bp.show_project', userid=uid, project_name=title))
    return render_template(
        'project_new.html',
        form=form,
        title='Create New Project'
    )


@login_required
@main_bp.route('/<int:userid>/<project>/new/page', methods=['GET', 'POST'])
def new_page(userid, project):
    """Create a new page."""
    # Check authorization
    if userid != current_user.id:
        print(f'Unauthorized user with ID <{current_user.id}>')
        return "You're not allowed to make new articles in this project."
    # Confirm project is real
    project = url_to_title(project)
    project = get_project_by_title(userid, project)
    if not project:
        return "There is no project with that name."
    set_project(project)

    form = forms.Page()
    if form.validate_on_submit():
        # Validate and alter the body text
        text = sanitize_text(project, form.text.data)
        print(text)
        # Create page
        page = create_page(
            db,
            userid,
            project,
            form.path.data,
            form.title.data,
            form.public.data,
            text
        )
        # If page is False, then there was already an article at that path
        if not page:
            form.title.errors = ['A page with this title already exists at that location.']
    else:
        for field, error in form.errors.items():
            print(f"{field}: {error}")
    return render_template(
        'page_new.html',
        form=form,
        title='Create New Page'
    )

@login_required
@main_bp.route('/content/edit/<id>', methods=['GET', 'POST'])
def edit_page(id):
    form = forms.PageEdit()
    page = m.Page.query.get(id)
    # Redirect if no page found
    if not page:
        return abort(404)
    # Make sure the user is allowed to access this page
    if page.owner_id != current_user.id:
        return abort(403)
    if form.validate_on_submit():
        # Alter Page
        project = m.Project.query.get(page.project_id)
        page.title = form.title.data
        page.public = form.public.data
        page.text = sanitize_text(project, form.text.data)
        db.session.commit()
        return redirect(url_for('main_bp.show_page_by_id', id=id))
    form.from_obj(page)
    return render_template(
        'edit_page.html',
        form = form,
        title = f'Editing {page.title}',
        page = page
    )

@main_bp.route('/<int:userid>/<project_name>/show/<path:path>', methods=['GET'])
def show_page(userid, project_name, path):
    # Sanitize input
    project_name = url_to_title(project_name)
    path = url_to_title(path)
    # Find the page in question
    project = get_project_by_title(userid, project_name)
    if not project:
        return abort(404)
    set_project(project)
    tree = get_project_tree(project)
    print(path)
    page = get_page_by_abs_path(project, path)
    # Display error if page not found or is private and we're not the owner
    if not page or (not page.public and current_user.id != page.owner_id):
        return abort(404)
    return render_template('page_show.html',
        title=page.title,
        page = page,
        pages = tree
    )

@main_bp.route('/<int:userid>/<project_name>/show/', methods=['GET'])
def show_project(userid, project_name):
    # Sanitize input
    project_name = url_to_title(project_name)
    # Get project, and then the page we need to display
    project = get_project_by_title(userid, project_name)
    if not project:
        abort(404)
    set_project(project)
    page = m.Page.query.get(project.page_id)
    if not page:
        abort(404)
    return render_template('page_show.html',
        title = project.title,
        page = page
    )

@main_bp.route('/show_page_by_id/<int:id>', methods=['GET'])
def show_page_by_id(id):
    page = m.Page.query.get(id)
    if not page:
        return not_found()
    project, path = get_path_from_id(page.id)
    return redirect(url_for(
        'main_bp.show_page',
        userid = page.owner_id,
        project_name = project,
        path = path
    ))

@main_bp.route('/login')
def login():
    print(request.args.get('next'))
    return redirect(url(ority_url + 'signin', next=request.args.get('next')))

@main_bp.route('/signup')
def signup():
    print(request.args.get('next', default=''))
    return redirect(url_for('http://localhost:5001/signup', next=request.args.get('next')))

def not_found():
    return render_template('404.html')

def url(endpoint, **values):
    for key, item in values.items():
        if item is None:
            continue
        endpoint += f'?{key}={item}'
    return endpoint

def set_project(p):
    if not p:
        pass
    session['project'] = {
        'id': p.id,
        'title': p.title,
        'owner_id': p.owner_id,
        'public': p.public,
        'page_id': p.page_id,
        'date_created': p.date_created,
        'date_modified': p.date_modified,
    }
    print(session['project']['title'])

'''
Accepts Markdown text and looks for link targets starting with "page:", then converts them to links starting with "id:".
'''
def sanitize_text(project, text):
    def replace(match):
        assert len(match.groups()) > 0
        arg = match.group(1)
        # If just a title, find the first corresponding page
        if r'/' not in arg:
            page = m.Page.query.filter_by(project_id=project.id, title=arg).first()
            assert page
        # Else get the id from the path
        else:
            page = get_page_by_abs_path(project, arg)
            assert page
        return f'(show_page_by_id/{page.id})'
    pattern = re.compile(r'\(page\:(.*?)\)')
    return pattern.sub(replace, text)