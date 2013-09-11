'''
Created on Sep 11, 2013

@author: gluedig
'''
from fm_services import app
import fm_services.db.message
from fm_services.db.message import messageDb
from fm_services.db.sql import Base
from fm_services.db.sql.sqllite import sql_session
import datetime

from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, DateTime
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

class messageDb(fm_services.db.message.messageDb):
    class Message(Base, fm_services.db.message.messageDb.Message):
        __tablename__ = 'messages'
        msg_id = Column(Integer, Sequence('msg_id_seq'), primary_key=True)
        text = Column(String(500))
        posted = Column(DateTime())
        user = Column(Integer, ForeignKey('users.user_id'))
        hub = Column(Integer, ForeignKey('hubs.hub_id'))

        def __init__(self, user_id, hub_id, text):
            self.text = text
            self.posted = datetime.datetime.now()
            self.user = user_id
            self.hub = hub_id

    def post(self, user_id, hub_id, text):
        new_msg = self.Message(user_id, hub_id, text)
        self.session.add(new_msg)
        self.session.commit()
        return new_msg

    def get(self, msg_id):
        try:
            msg = self.session.query(self.Message).filter(self.Message.msg_id == msg_id).one()
            return msg 
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None
        
        return None
    
    def update(self, msg_id, text):
        msg = self.get(msg_id)
        if not msg:
            return None
        else:
            msg.text = text
            self.session.update(msg)
            self.session.commit()
            return msg
            
    def remove(self, msg_id):
        msg = self.get(msg_id)
        if not msg:
            return False
        else:
            self.session.remove(msg)
            self.session.commit()
            return True
        
    def get_by_user(self, user_id, count=False, start=0, end=-1):
        try:
            if count:
                msg_no = self.session.query(self.Message)\
                .filter(self.Message.user == user_id)\
                .order_by(self.Message.mgs_id).count()
                return [msg_no]
            else:
                msgs = self.session.query(self.Message)\
                .filter(self.Message.user == user_id)\
                .order_by(self.Message.mgs_id)[start:end]
            
                return msgs 
        except NoResultFound:
            return None
        
        return None
    
    def get_by_hub(self, hub_id, count=False, start=0, end=-1):
        try:
            if count:
                msg_no = self.session.query(self.Message)\
                .filter(self.Message.hub == hub_id)\
                .order_by(self.Message.mgs_id).count()
                return [msg_no]
            else:
                msgs = self.session.query(self.Message)\
                .filter(self.Message.hub == hub_id)\
                .order_by(self.Message.mgs_id)[start:end]
            
                return msgs 
        except NoResultFound:
            return None
        
        return None
    
    def __init__(self):
        self.session = sql_session

app.db['messages'] = messageDb()