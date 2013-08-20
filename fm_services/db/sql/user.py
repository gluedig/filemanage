'''
Created on Aug 20, 2013

@author: gluedig
'''
from fm_services import app
import fm_services.db.user
from fm_services.db.user import userDb
from fm_services.db.sql import Base, Session
import datetime

from sqlalchemy import Column, Integer, String, Sequence, DateTime
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

class userDb(fm_services.db.user.userDb):
    
    class User(Base, fm_services.db.user.userDb.User):
        __tablename__ = 'users'
        user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
        firstname = Column(String(50))
        lastname = Column(String(50))
        email = Column(String(50))
        image = Column(String(50))
        password = Column(String(50))
        created = Column(DateTime())
        modified = Column(DateTime())
        seen = Column(DateTime())
        
        def __init__(self, email, image):
            now = datetime.datetime.now()
            self.created = now
            self.modified = now
            self.seen = now
            
            self.firstname = ''
            self.lastname = ''
            self.password = None
            
            self.image = image
            self.email = email
            
    
    def add(self, email, passwd, image):
        new_user = self.User(email, image)
        new_user.set_password(passwd)
        self.session.add(new_user)
        self.session.commit()
        return new_user
        
    def find_by_id(self, user_id):
        try:
            user = self.session.query(self.User).filter(self.User.user_id == user_id).one()
            return user 
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None
        
        return None
        
    def find_by_name(self, user_name):
        try:
            user = self.session.query(self.User).filter(self.User.email == user_name).one()
            return user 
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None
        
        return None
    
    def login(self, user_id):
        user = self.find_by_id(user_id)
        if user:
            user.seen = datetime.datetime.now()

    def __init__(self):
        self.session = Session()
    
app.db['users'] = userDb()
    
    