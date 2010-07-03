from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Index
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper, sessionmaker, relation, backref, deferred,\
                           undefer_group, column_property, validates, scoped_session
from sqlalchemy.sql import func
from contextlib import contextmanager

engine = create_engine('sqlite:///flask_sqla_wiki.sqlite', echo=True)
metadata = MetaData()

#@contextmanager
#def magic_session(thing):
#    session = Session.object_session(thing) or Session()
#    yield session
#    if session != Session.object_session(thing): session.close()

Session = scoped_session(sessionmaker(bind=engine, autocommit=False))

pages_table = Table("pages", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True)
)

page_name_idx = Index("page_name", pages_table.c.name);

versions_table = Table("versions", metadata,
    Column("rev", Integer, primary_key=True),
    Column("page_id", Integer, ForeignKey("pages.id"), nullable=False),
    Column("title", String, nullable=False),
    Column("content", String, nullable=False)
)

version_page_id_idx = Index("version_page_id", versions_table.c.page_id);


tags_table = Table("tags", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True)
)

tag_name_idx = Index("tag_name", tags_table.c.name);

pages_tags_table = Table("pages_tags", metadata,
    Column("page_id", Integer, ForeignKey("pages.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

metadata.create_all(engine)


class Version(object):
    def __init__(self, title, content):
        self.title = title
        self.content = content


class Page(object):
    def __init__(self, name): self.name = name
    def __repr__(self): return "<Page('%s')>" % (self.name)
    def tag_list(self): return [tag.name for tag in self.tags]
    def _get_tag_string(self): return ", ".join(self.tag_list())
    def _set_tag_string(self, string):
        tags = set((tag.strip(" ").lower() for tag in string.split(",")))
        if "" in tags: tags.remove("")
        #with magic_session(self) as session:
        existing_tags = Session.query(Tag).filter(Tag.name.in_(tags)).all()
        for tag in existing_tags: tags.remove(tag.name)
        for tag in tags: existing_tags.append(Tag(tag))
        self.tags = existing_tags
    tag_string = property(_get_tag_string, _set_tag_string)


class Tag(object):
    def __init__(self, name): self.name = name

    @staticmethod
    def all():
        tags = Session().query(Tag.name).filter(Tag.pages.any())
        return [tag.name for tag in tags.all()]

    @validates("name")
    def validate_name(self, key, name):
        assert name == name.lower()
        return name


mapper(Version, versions_table, properties={
    "content": deferred(versions_table.c.content, group="text"),
    "title": deferred(versions_table.c.title, group="text")
})

mapper(Tag, tags_table)

mapper(Page, pages_table, properties={
    "versions": relation(Version, backref="page", order_by=Version.rev.desc),
    "tags": relation(Tag, secondary=pages_tags_table, backref="pages", lazy=False)
})

