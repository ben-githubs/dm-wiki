from datetime import datetime
import re

from flask_login import UserMixin

re_timestamp = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$')

def dict_to_obj(d, obj=object):
    # Load dictionary and return an object
    for key, val in d.items():
        # If val is in ISO format, then cast to datetime
        if isinstance(val, str) and re_timestamp.match(val):
            val = datetime.fromisoformat(val)
        setattr(obj, key, val)

class User(UserMixin):
    def __init__(self, **kwargs):
        dict_to_obj(kwargs, self)
        assert hasattr(self, 'id'), "User object must specify an ID!"