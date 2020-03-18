from hashlib import pbkdf2_hmac


if __name__ != "__main__":
    from sys import path
    path.append(path[0] + '\\data')


from connections import Base, create_session
from tables import *


def register_user(name, email, password):
    session = create_session()
    user = User()
    user.name = name
    user.email = email
    user.hashed_password = pbkdf2_hmac('sha512', password, b'bytes', 10)
    session.add(user)