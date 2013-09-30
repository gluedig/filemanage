'''
Created on Sep 10, 2013

@author: gluedig
'''
from fm_services import app
import fm_services.db.hub
#from fm_services.db.hub import hubDb
from fm_services.db.sql.user import userDb
from fm_services.db.sql import Base
from fm_services.db.sql.sqllite import sql_session

from sqlalchemy import Column, Integer, String, Sequence, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


associations_table = Table('hub_associations', Base.metadata,
                Column('user', Integer, ForeignKey('users.user_id'), primary_key=True, nullable=False),
                Column('hub', Integer, ForeignKey('hubs.hub_id'), primary_key=True, nullable=False)
                )

class hubDb(fm_services.db.hub.hubDb):
    class Hub(Base, fm_services.db.hub.hubDb.Hub):
        __tablename__ = 'hubs'
        hub_id = Column(Integer, Sequence('hub_id_seq'), primary_key=True)
        description = Column(String(50))
        
        associations = relationship('User', 
                    secondary=associations_table
        )
        
        def __init__(self, description):
            self.description = description
    
    def create_hub(self, description):
        new_hub = self.Hub(description)
        self.session.add(new_hub)
        self.session.commit()
        return new_hub
    
    def get_hub(self, hub_id):
        try:
            hub = self.session.query(self.Hub).filter(self.Hub.hub_id == hub_id).one()
            return hub
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None
        
        return None

    def find_hubs(self, user_id):
        hubs = self.session.query(self.Hub).filter(self.Hub.associations.any(user_id=user_id)).all()
        return hubs
    
    def associate(self, hub_id, user_id, only=False):
        user = app.db['users'].find_by_id(user_id)
        hub = self.get_hub(hub_id)
        if user and hub:
            if only:
                hubs = self.find_hubs(user_id)
                for x in hubs:
                    x.associations.remove(user)

            hub.associations.append(user)
            self.session.commit()
            return True
        else:
            return False

    def unassociate(self, hub_id, user_id):
        user = app.db['users'].find_by_id(user_id)
        hub = self.get_hub(hub_id)
        if user and hub:
            if user in hub.associations:
                hub.associations.remove(user)
                self.session.commit()
            return True
        else:
            return False

    def get_users(self, hub_id):
        try:
            users = self.session.query(associations_table, userDb.User)\
                .filter_by(hub=hub_id)\
                .join(userDb.User)\
                .all()
            return [user for _, _, user in users]
        except NoResultFound:
            return None
        
        return None

    def __init__(self):
        self.session = sql_session
    
app.db['hubs'] = hubDb()