from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Index
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper, sessionmaker, relation, relationship, backref, deferred,\
                           undefer_group, column_property, validates, scoped_session
from sqlalchemy.sql import func, select
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta, synonym_for
from contextlib import contextmanager
from wiki import Base


#page_name_idx = Index("page_name", pages_table.c.name);

#version_page_id_idx = Index("version_page_id", versions_table.c.page_id);

#tag_name_idx = Index("tag_name", tags_table.c.name);


pages_tags_table = Table("pages_tags", Base.metadata,
    Column("page_id", Integer, ForeignKey("pages.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)


#create_all()


class Version(Base):
    __tablename__ = "versions"
    rev = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    title = Column(String, nullable=False)
    content = deferred(Column(String, nullable=False))
    
    def __init__(self, title, content):
        self.title = title
        self.content = content


class Tag(Base):
    __tablename__ = "tags"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False, unique=True)

    def __init__(self, name): self.name = name

    @staticmethod
    def all():
        tags = Tag.query.filter(Tag.pages.any()) # don't need .all() here?
        return [tag.name for tag in tags]

    @validates("name")
    def validate_name(self, key, name):
        assert name == name.lower()
        return name





class Page(Base):
    ##__tablename__ = "pages"
    __table__ = Table("pages", Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False, unique=True)
    )
    versions = relation(Version, backref="page", order_by=Version.rev.desc)
    tags = relation(Tag, secondary=pages_tags_table, backref="pages", lazy="subquery")

    max_rev_query = select(
        [
            Version.page_id.label("eddie"),
            func.max(Version.rev).label("max_rev")
        ],
        group_by=Version.page_id
    )
    
    _latest_version = relationship(Version,
        secondary=max_rev_query,
        primaryjoin = max_rev_query.c.eddie == __table__.c.id,
        secondaryjoin = max_rev_query.c.max_rev == Version.rev,
        foreign_keys = [max_rev_query.c.eddie, max_rev_query.c.max_rev],
        lazy=False,
        viewonly=True)
    
    @synonym_for('_latest_version')
    @property
    def latest_version(self):
        return self._latest_version[0]
    
    def __init__(self, name): self.name = name
    def __repr__(self): return "<Page('%s')>" % (self.name)
    #def tag_list(self): return [tag.name for tag in self.tags]
    def _get_tag_string(self): return ", ".join([tag.name for tag in self.tags])
    def _set_tag_string(self, string):
        tags = set((tag.strip(" ").lower() for tag in string.split(",")))
        if "" in tags: tags.remove("")
        existing_tags = Tag.query.filter(Tag.name.in_(tags)).all() # need .all() here?
        for tag in existing_tags: tags.remove(tag.name)
        for tag in tags: existing_tags.append(Tag(tag))
        self.tags = existing_tags
    tag_string = property(_get_tag_string, _set_tag_string)
    






































