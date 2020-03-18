import datetime
from sqlalchemy import BigInteger, String, DateTime, Column, Date, ForeignKey, Table
from connections import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_date = Column(Date, default=datetime.datetime.now)

class Connector(Base):
    __tablename__ = 'connector'
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    dial_id = Column(BigInteger, ForeignKey('dialogs.id', ondelete="CASCADE"), primary_key=True)

class Dialog(Base):
    __tablename__ = 'dialogs'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, index=True, nullable=True)
    file = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.now)
