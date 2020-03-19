import datetime
from sqlalchemy import Integer, String, DateTime, Column, Date, ForeignKey, Table, Boolean, orm, LargeBinary, Table, MetaData


if __name__ != "__main__":
    from sys import path
    path.append(path[0] + '\\data')


from connections import Base


connector = Table(
    'connector', MetaData(),
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('dial_id', Integer, ForeignKey('dialogs.id', ondelete="CASCADE"), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, index=True, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(LargeBinary, nullable=True)
    created_date = Column(Date, default=datetime.datetime.now)
    dialogs = orm.relation('Dialog', secondary=connector, back_populates="users")

class Dialog(Base):
    __tablename__ = 'dialogs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    many_people = Column(Boolean, default=False)
    hashed_password = Column(LargeBinary, nullable=True)
    dialogs = orm.relation('User', secondary=connector, back_populates="dialogs")
