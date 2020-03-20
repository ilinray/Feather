from hashlib import pbkdf2_hmac
from pathlib import Path
from datetime import datetime
from csv import writer, reader


if __name__ != "__main__":
    from sys import path
    path.append(path[0] + '\\data')


from tables import *
from connections import Base, create_session, global_init


global_init('db/featherDB.sqlite')
session = create_session()
dialogs_path = Path.cwd()
if dialogs_path.stem == 'data':
    dialogs_path = Path.cwd().parent
dialogs_path.joinpath('dialogs')


def hashed_password(password):
    return pbkdf2_hmac('sha512', bytes(password, 'u8'), bytes('bytes', 'u8'), 10)


def check_password(password, user_id):
    session = create_session()
    return session.query(User).get(user_id).hashed_password == hashed_password(password)


class Message:
    def __init__(self, user_id, text, files, datetime):
        self.text = text
        self.files = files
        self.user_id = user_id
        self.datetime = datetime.today()

    def add2file(self, directory):
        path = dialogs_path.joinpath(
            directory, self.datetime.date().isoformat()).with_suffix('.csv')
        with path.open('a') as fi:
            writer(fi, deltimeter=';').writerow((self.user_id,
                                                 self.text,
                                                 ','.join(self.files),
                                                 self.datetime.timestamp(timespec='seconds')))


class UserConnector:
    def __init__(self, user):
        self.entry = user
        self.id = user.id

    @classmethod
    def from_id(cls, user_id):
        try:
            return cls(session.query(User).get(user_id))
        except:
            return None

    @classmethod
    def new_user(cls, login, email, password):
        user = User()
        user.login = login
        user.email = email
        user.hashed_password = hashed_password(password)
        session.add(user)
        session.commit()
        return cls(user)

    def check_password(self, password):
        return hashed_password(password) == self.entry.hashed_password

    @classmethod
    def login(cls, login, password):
        user = cls(session.query(User).filter(User.login == login).first())
        if user.check_password(password):
            return user

class DialogConnector:
    def __init__(self, dialog):
        self.entry = dialog
        self.id = dialog.id

    @classmethod
    def from_id(cls, dialog_id):
        return cls(session.query(Dialog).get(dialog_id))

    @classmethod
    def new_dialog(cls, *users_id, name=None, password=None):
        dialog = Dialog()
        if len(users_id) > 2:
            dialog.many_people = True
        elif len(users_id) == 2:
            dialog.many_people = False
        else:
            raise Exception('Strange amount of users')
        dialog.name = name
        if password is not None:
            dialog.hashed_password = hashed_password(password)
        session.add(dialog)
        session.commit()
        path = dialogs_path.joinpath(str(dialog.id))
        path.mkdir(parents=True, exist_ok=True)
        for id in users_id:
            entry = Connector()
            entry.user_id = id
            entry.dial_id = dialog.id
            session.add(entry)
        session.commit()
        return cls(dialog)

    def get_users_id(self):
        return session.query(Connector).filter(Connector.dialog_id == self.id)

    def get_log_directory(self):
        return self.entry.directory

    def get_messages(self):
        for path in dialogs_path.joinpath(str(self.id)).itemdir():
            with path.open('r') as fi:
                for row in reader(fi, deltimeter=';'):
                    yield Message(row[0], row[1], row[2].split(','), datetime.fromisoformat(row[3]))

    def has_password(self):
        return self.entry.hashed_password is not None

    def check_password(self, password):
        return self.entry.hashed_password == hashed_password(password)

    def send_msg(self, message):
        message.add2file(str(self.entry.id))


# DialogConnector.new_dialog(
#     UserConnector.new_user('q', 'lmaao', 'lmao').id,
#     UserConnector.new_user('lmao', 'lmao', 'lmao').id
# )