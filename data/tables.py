# This file contains all DB tables


import datetime
from sqlalchemy import (Integer, String, DateTime, Column,
                        Date, ForeignKey, Table, Boolean,
                        orm, LargeBinary, Table, MetaData)
from .connections import Base


# Connects User to a Dialog. Needed for many2many relationship
class Connector(Base):
    __tablename__ = 'connector'
    user_id = Column(Integer, ForeignKey(         # user
        'users.id', ondelete="CASCADE", onupdate='CASCADE'), primary_key=True)
    dial_id = Column(Integer, ForeignKey(         # dialog
        'dialogs.id',
        ondelete="CASCADE",
        onupdate='CASCADE'), primary_key=True)
    user = orm.relationship("User", back_populates="dialogs")
    dialog = orm.relationship("Dialog", back_populates="users")
    # some orm sqlalchemy features


# This table contains users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)  # id of user
    login = Column(String, index=True, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(LargeBinary)   # Password is hashed
    has_pic = Column(Boolean, default=False)  # If user set his profie pic
    created_date = Column(Date, default=datetime.datetime.now)
    dialogs = orm.relation('Connector', back_populates='user')


# This table contains all dialogs
class Dialog(Base):
    __tablename__ = 'dialogs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    has_pic = Column(Boolean, default=False)  # If host set dialog pic
    host_id = Column(Integer, ForeignKey(    # User who created a dialog
        'users.id', ondelete='SET NULL', onupdate='SET NULL'), nullable='True')
    host = orm.relation('User')
    users = orm.relation('Connector', back_populates='dialog')
    messages = orm.relation('Message', back_populates='dialog')


# This table contains all messages
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, index=True, nullable=True)
    dialog_id = Column(Integer, ForeignKey(  # dialog in what msg was sent
        'dialogs.id', ondelete='CASCADE', onupdate='CASCADE'))
    dialog = orm.relation('Dialog', back_populates='messages')
    user_id = Column(Integer, ForeignKey(  # User who wrote a message
        'users.id', ondelete='SET NULL', onupdate='SET NULL'), nullable='True')
    user = orm.relation('User')
    created_date = Column(DateTime, default=datetime.datetime.now)
    files = orm.relation('File')  # files, which were attached to msg


# This table contains info about files, which were sent in all dialogs
class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String)  # initial name of file
    file_access = Column(Integer)  # id of dialog for checking access
    message_id = Column(Integer, ForeignKey(  # msg id, what contains a file
        'messages.id', ondelete='CASCADE', onupdate='CASCADE'))
