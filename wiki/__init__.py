from flask import Flask, render_template, request, redirect, url_for
from pdb import set_trace
from sqlalchemy.exc import InvalidRequestError


################################################################################
## Database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

engine = create_engine('sqlite:///flask_sqla_wiki.sqlite', echo=True)
session = Session = scoped_session(sessionmaker(bind=engine, autocommit=False))

class QueryProperty(object):
    def __get__(self, instance, owner):
        return session.query(owner)

class QueryPropertyMeta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
        cls.query = QueryProperty()
        return DeclarativeMeta.__init__(cls, classname, bases, dict_)
        
class EggFooYung(object):
    eezer = "sneezer"
    query = QueryProperty()

Base = declarative_base(bind=engine,
                        #metaclass=QueryPropertyMeta,
                        cls=EggFooYung)


################################################################################
## App object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_sqla_wiki.sqlite'

@app.after_request
def save_session(response):
    try:
        session.commit()
    except InvalidRequestError:
        # no transaction outstanding
        pass
    finally:
        session.close()
        
    return response

@app.errorhandler(500)
def rollback(error):
    print "ROLLLBAAAAACK"
    try:
        session.rollback()
    except InvalidRequestError:
        # no transaction outstanding
        pass
    

import wiki.views











































