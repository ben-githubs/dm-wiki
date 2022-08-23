from .models import Page, Project

def url_to_title(s):
    """ Converts an encoded URL segment into a page title. """
    return s.replace('_', ' ')

def title_to_url(s):
    """ Does the inverse of the above fcn. """
    return s.replace(' ', '_')

def get_projects_by_owner(owner_id):
    assert isinstance(owner_id, int)
    return Project.query.filter_by(owner_id=owner_id).all()

def get_project_by_title(owner_id, title):
    assert isinstance(owner_id, int)
    assert isinstance(title, str)
    return Project.query.filter_by(owner_id=owner_id, title=title).first()

def get_child_page_by_title(page, title):
    if not page.children:
        return None
    for child in page.children:
        if child.title == title:
            return child
    return None # Return none if there is no match

def get_page_by_rel_path(root, path):
    """ Given a Page object, and a file path, returns the Page at path. """
    parts = path.split('/')

    page = root
    while parts:
        child = get_child_page_by_title(page, parts[0])
        if child is None:
            return None
        parts.pop(0) # Remove the top layer
        page = child
    return page

def get_page_by_abs_path(project, path):
    page = Page.query.get(project.page_id)
    return get_page_by_rel_path(page, path)

def can_view_page(project, page, userid):
    """ Determines if a user is allowed to view the page. Checks ownership and view permissions. """
    return is_page_owner(page, userid) or (project.public and page.public)

def is_page_owner(page, userid):
    return page.owner_id == userid

def create_page(db, userid, proj, path, title, public=True, text=''):
    assert proj # Make sure it exists
    parts = path.split('/')
    parts.append(title)
    parts = [p.strip() for p in parts if p] # Remove empty fields
    print(parts)
    # Since we're using a loop, and the loop makes dummy pages for all the parents, we want to set their
    # text to null, and keep the content for the last page.
    text_arr = ['']*len(parts)
    text_arr[-1] = text
    # We get our root-level page, ready for the loop below. We know this page should exist.
    parent = Page.query.get(proj.page_id)
    # We want to make sure we actually do create a new page. If this page already exists, then we'll leave
    # this as false and return it to let the user know we had a problem.
    page_created = False

    # Now, we loop through each part of the path, and create a dummy page for it if there isn't one already.
    for i in range(len(parts)):
        # See if this page exists
        this_page = get_child_page_by_title(parent, parts[i])
        # Create this page if necessary
        if not this_page:
            this_page = Page(title=parts[i], public=public, owner_id=userid, text=text_arr[i], parent=parent, project_id=proj.id)
            db.session.add(this_page)
            db.session.commit()
            if i == len(parts)-1: page_created = True
        parent = this_page
    return this_page if page_created else False
    
def get_path_from_id(page_id):
    path = list()
    page = Page.query.get(page_id)
    assert page, f"No Page with ID <{page_id}>."
    first_iter = True # Simulate a do-while loop
    while page.parent:
        first_iter = False
        path.insert(0, title_to_url(page.title))
        page = page.parent
    # Now we have a root page. This should correspond to the project root,
    project = Project.query.filter_by(page_id = page.id).first()
    path.insert(0, title_to_url(page.title))
    assert project, f"Page <{page.id}> has no project!"
    return title_to_url(project.title), '/'.join(path[1:]) # path[0] is project name

"""
Returns a tree structure of all pages.
"""
def get_project_tree(project):
    all_pages = Page.query.filter_by(project_id = project.id).all()
    # Get root page
    root = [p for p in all_pages if not p.parent_id][0]
    def page_to_dict(page):
        data = {
            'id': page.id,
            'title': page.title,
            'children': [page_to_dict(p) for p in all_pages if p.parent_id == page.id]
        }
        return data
    return page_to_dict(root)






    def recur(db, userid, path, title, public=True, text=''):
        print(path)
        parts = path.split('/')
        new_path = '/'.join(parts[:-1])
        title = parts[-1]
        parent = get_page_by_abs_path(proj, new_path)
        if not parent:
            parent = recur(db, userid, new_path, title)
        page = Page(title=title, public=public, text=text, owner_id=userid)
        page.parent = parent
        db.session.add(page)
        db.session.commit()
        return page
    recur(db, userid, path, title, public, text)
