import datetime
from sqlalchemy import Integer, String, DateTime, Column, Date, ForeignKey, Table, Boolean, orm, LargeBinary, Table, MetaData


if __name__ != "__main__":
    from sys import path
    path.append(path[0] + '\\data')


from connections import Base


class Connector(Base):
    __tablename__ = 'connector'
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    dial_id = Column(Integer, ForeignKey('dialogs.id', ondelete="CASCADE"), primary_key=True)
    user = orm.relationship("User", back_populates="dialogs")
    dialog = orm.relationship("Dialog", back_populates="users")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, index=True, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(LargeBinary, nullable=True)
    has_pic = Column(Boolean, default=False)
    created_date = Column(Date, default=datetime.datetime.now)
    dialogs = orm.relation('Connector', back_populates='user')

class Dialog(Base):
    __tablename__ = 'dialogs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    many_people = Column(Boolean, default=False)
    hashed_password = Column(LargeBinary, nullable=True)
    has_pic = Column(Boolean, default=False)
    users = orm.relation('Connector', back_populates='dialog')
