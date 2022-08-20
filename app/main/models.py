from sqlalchemy import ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import TypeDecorator, VARCHAR

from .paths import Path

from .. import db

"""TSVector is needed for full-test search. Find info in it here"
https://amitosh.medium.com/full-text-search-fts-with-postgresql-and-sqlalchemy-edc436330a0c
"""
class TSVector(TypeDecorator):
    impl = TSVECTOR

class PathType(TypeDecorator):
    impl = VARCHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return str(value)
    
    def process_result_value(self, value, dialect):
        return Path(value)

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), index=True)
    owner_id = db.Column(db.Integer, index=True)
    public = db.Column(db.Boolean, default=False)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'))

    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_modified = db.Column(db.DateTime(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())

class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), index=True)
    owner_id = db.Column(db.Integer, index=True)
    public = db.Column(db.Boolean, default=False)
    text = db.Column(db.Text, nullable=True)

    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_modified = db.Column(db.DateTime(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())

    parent_id = db.Column(db.Integer, ForeignKey('pages.id'))
    parent = db.relationship("Page", backref=db.backref("children"), remote_side=[id], single_parent=True, cascade="all, delete-orphan",)

    project_id = db.Column(db.Integer, ForeignKey('projects.id'), index=True, nullable=False)
    
    __ts_vector__ = db.Column(TSVector(), db.Computed("to_tsvector('english', title || ' ' || text)", persisted=True))
    __table_args__ = (Index('ix_video___ts_vector__', __ts_vector__, postgresql_using='gin'),)