'''
Created on Aug 20, 2013

@author: gluedig
'''
from fm_services import app
from fm_services.db.sql import Session, Base
from sqlalchemy import create_engine

engine = create_engine('sqlite:///fm_services.db', echo=app.config['SQL_ECHO'])
Session.configure(bind=engine)
Base.metadata.bind = engine
sql_session = Session()