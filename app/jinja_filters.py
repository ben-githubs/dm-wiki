from markdown import markdown as _markdown
from jinja2.filters import do_mark_safe

def markdown(value):
    return do_mark_safe(_markdown(value))