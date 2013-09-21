'''
Created on Aug 20, 2013

@author: gluedig
'''
from fm_services import app
import fm_services.db.user
from fm_services.db.user import userDb
from fm_services.db.sql import Base
from fm_services.db.sql.sqllite import sql_session
import datetime

from sqlalchemy import Column, Integer, String, Sequence, DateTime, Table, ForeignKey, or_
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import IntegrityError

contacts_table = Table('contacts', Base.metadata,
                Column('owner', Integer, ForeignKey('users.user_id'), primary_key=True),
                Column('contact', Integer, ForeignKey('users.user_id'), primary_key=True)
                )

class userDb(fm_services.db.user.userDb):
#    class ContactsList(Base):
#        __tablename__ = 'contacts'
#        owner = Column('owner', Integer, ForeignKey('users.user_id'), primary_key=True)
#        contact = Column('contact', Integer, ForeignKey('users.user_id'))
#        
    class User(Base, fm_services.db.user.userDb.User):
        __tablename__ = 'users'
        user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
        firstname = Column(String(50))
        lastname = Column(String(50))
        email = Column(String(50), unique=True)
        image = Column(String(50))
        password = Column(String(50))
        created = Column(DateTime())
        modified = Column(DateTime())
        seen = Column(DateTime())
        
        contacts = relationship('User', 
                    secondary=contacts_table,
                    primaryjoin=('users.c.user_id == contacts.c.owner'),
                    secondaryjoin=('users.c.user_id == contacts.c.contact'),
        )
        
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
        try:
            self.session.add(new_user)
            self.session.commit()
            return new_user
        except IntegrityError:
            self.session.rollback()
            return None

        return None
        
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
    
    def find(self, search_term):
        try:
            users = self.session.query(self.User)\
                .filter(or_(self.User.email == search_term,\
                            self.User.lastname.like('%'+search_term+'%'),\
                            self.User.firstname.like('%'+search_term+'%'))).all()
            return users
        except MultipleResultsFound:
            return []
        except NoResultFound:
            return []

        return []

    def login(self, user_id):
        user = self.find_by_id(user_id)
        if user:
            user.seen = datetime.datetime.now()
    
    def get_contacts(self, user_id):
        user = self.find_by_id(user_id)
        if user:
            return user.contacts
        else: 
            return []
    
    def add_contact(self, user_id, contact):
        user = self.find_by_id(user_id)
        contact = self.find_by_id(contact)
        if user and contact:
            user.contacts.append(contact)
            self.session.commit()
            return True
        else:
            return False
    
    def remove_contact(self, user_id, contact):
        user = self.find_by_id(user_id)
        contact = self.find_by_id(contact)
        if user and contact:
            user.contacts.remove(contact)
            self.session.commit()
            return True
        else:
            return False

    def __init__(self):
        self.session = sql_session
    
app.db['users'] = userDb()
    
    