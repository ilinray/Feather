from hashlib import pbkdf2_hmac


if __name__ != "__main__":
    from sys import path
    path.append(path[0] + '\\data')


from connections import Base, create_session
from tables import *


def hashed_password(password):
    return pbkdf2_hmac('sha512', password, b'bytes', 10)


def register_user(name, email, password):
    session = create_session()
    user = User()
    user.name = name
    user.email = email
    user.hashed_password = hashed_password(password)
    session.add(user)
    session.commit()

def get_user_id(login):
    session = create_session()
    return session.query(User).filter(User.login == login).first().id

def check_password(password, user):
    session = create_session()
    # не доделано
