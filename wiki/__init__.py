from flask import Flask, render_template, request, redirect, url_for
from pdb import set_trace


################################################################################
## App object

class MyFlask(Flask):
    def handle_exception(self, e):
        print
        print "\nCUSTOM HANDLER EXCEPTION\n"
        print
        session.close()
        Flask.handle_exception(self, e)

app = MyFlask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://flaskywiki:flaskywiki@localhost/flaskywiki')
#sqlite:///flask_sqla_wiki.sqlite
#mysql://flaskywiki:flaskywiki@localhost/flaskywiki


################################################################################
## Database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.interfaces import MapperExtension

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
session = Session = scoped_session(sessionmaker(bind=engine, autocommit=False))

class QueryProperty(object):
    def __get__(self, instance, owner):
        return session.query(owner)

class MyBaseBase(object):
    query = QueryProperty()

Base = declarative_base(bind=engine, cls=MyBaseBase)


@app.after_request
def save_session(response):
    print "\nSAVING SESSION\n"
    try:
        session.commit()
    except:
        session.close()
    return response

@app.errorhandler(500)
def rollback(error):
    print "\nROLLLBAAAAACK\n"
    try:
        session.close()
    except InvalidRequestError:
        # no transaction outstanding
        pass
    

import wiki.views









































