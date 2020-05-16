# This file contains classes which represent app objects
# Those are helping API to get data


from .connections import Base, create_session, global_init
from .tables import *
from hashlib import pbkdf2_hmac
from pathlib import Path
from datetime import datetime
from csv import writer, reader


if __name__ != "__main__":
    from sys import path
    path.append(path[0] + '\\data')


global_init('db/featherDB.sqlite')
session = create_session()

pic_formats = ('gif', 'png', 'jpg', 'jpeg')


def filetype(id):
    # returns type of file from id (img/file)
    f = FileConnector.from_id(id).entry.filename.rsplit(
        '.', maxsplit=1)[-1] in pic_formats
    return 'image' if f else 'file'


def hashed_password(password):
    # Hashes everything
    return pbkdf2_hmac('sha512',
                       bytes(password, 'u8'),
                       bytes('bytes', 'u8'), 10)


class BaseConnector:
    # Base class for app objects
    table = None  # Table which represents object
    table_attrs = set()  # Kwargs which are requred for .new method

    def __init__(self, entry):
        # Constructs object from it's DB entry
        self.id = entry.id
        self.entry = entry

    @classmethod
    def from_id(cls, id):
        # Returns object from it's id in DB
        try:
            return cls(session.query(cls.table).get(id))
        except:
            return None

    @classmethod
    def new(cls, table_attrs=None, **kwargs):
        # Inserts new entry to DB and return it's object
        entry = cls.table()
        if table_attrs is None:
            table_attrs = cls.table_attrs
        foo = table_attrs - set(kwargs.keys())
        if foo:
            raise TypeError(f'Wrong args. Not found: {foo}')
        for k in table_attrs:
            setattr(entry, k, kwargs[k])
        session.add(entry)
        session.commit()
        return cls(entry)

    @classmethod
    def exists_from_id(cls, id):
        # Checks if entry with given id exists
        return session.query(cls.table).get(id) is not None


class MessageConnector(BaseConnector):
    # Class of messages
    table = Message
    table_attrs = set(('text',
                       'user_id',
                       'created_date',
                       'dialog_id'))

    @classmethod
    def new(cls, files=[], **kwargs):
        # In addition creates files, which message has
        msg = super().new(table_attrs=cls.table_attrs, **kwargs)
        for f in files:
            FileConnector.register_file(kwargs['dialog_id'], f, msg.id)
        return msg

    def to_dict(self):
        # Returns all information about message
        files = []
        for file in self.entry.files:
            f = file.filename.rsplit('.', maxsplit=1)[-1] in pic_formats
            d = {'filename': file.filename,
                 'file_id': f'{file.file_access}_{file.id}',
                 'type': 'image' if f else 'file'}
            files.append(d)
        date = self.entry.created_date.isoformat(timespec='seconds')
        login = UserConnector.from_id(self.entry.user_id).entry.login
        retval = {'id': self.id,
                  'text': self.entry.text,
                  'uid': self.entry.user_id,
                  'datetime': date,
                  'files': files,
                  'login': login}
        return retval

    def delete(self):
        # delets messge from DB
        q = session.query(Message)
        q.filter(Message.id == self.id).delete()
        session.commit()


class FileConnector(BaseConnector):
    # Class which represents files
    table = File
    table_attrs = set(('filename',
                       'message_id',
                       'file_access'))

    @classmethod
    def register_file(cls, access, file, message_id):
        # Saves files from messages to hard drive
        id = cls.new(filename=file.filename,
                     message_id=message_id, file_access=access).id
        new_filename = f'{access}_{id}'
        file.save('user_imgs/' + new_filename)


class UserConnector(BaseConnector):
    # Class which represents user
    table = User
    table_attrs = set(('login',
                       'email',
                       'password'))

    @classmethod
    def new(cls, **kwargs):
        # Also hashes password
        user = super().new(table_attrs=cls.table_attrs, **kwargs)
        user.entry.hashed_password = hashed_password(kwargs['password'])
        return user

    def check_password(self, password):
        # Check if password is correct
        return hashed_password(password) == self.entry.hashed_password

    @classmethod
    def login(cls, login, password):
        # Returns user object from from his login and password
        entry = session.query(User).filter(User.login == login).first()
        if entry is None:
            return None
        user = cls(entry)
        if user.check_password(password):
            return user
        else:
            raise ValueError

    @property
    def chats(self):
        # Returns all chats of user
        for each in self.entry.dialogs:
            yield DialogConnector(each.dialog)

    @staticmethod
    def exists_from_login(login):
        # You can also check if login is taken
        q = session.query(User)
        return q.filter(User.login == login).first() is not None

    @classmethod
    def from_login(cls, login):
        # Returns user object from login
        entry = session.query(User).filter(User.login == login).first()
        if entry is not None:
            return cls(entry)

    @staticmethod
    def delete_by_id(id):
        # Deletes user
        session.query(User).filter(User.id == id).delete()
        session.commit()


class DialogConnector(BaseConnector):
    # Class represents dialog
    table = Dialog
    table_attrs = set(('host_id', 'name'))

    @classmethod
    def new(cls, **kwargs):
        # Also connects user to dialog
        if kwargs['name'] is None:
            kwargs['name'] = 'Chat'
        dialog = super().new(table_attrs=cls.table_attrs, **kwargs)
        for id in kwargs['users_id']:
            entry = Connector()
            entry.user_id = id
            entry.dial_id = dialog.id
            session.add(entry)
        session.commit()
        return dialog

    @property
    def users(self):
        # returns users of this dialog
        for each in self.entry.users:
            yield UserConnector(each.user)

    @property
    def users_id(self):
        # Returns ids of users in chat
        for each in self.entry.users:
            yield each.user_id

    def get_messages(self, count, offset):
        # Returns messages in reverse order with given offset and count
        query = session.query(Message)
        query = query.filter(Message.dialog_id == self.id).order_by(
            Message.id.desc()).offset(offset).limit(count)
        for each in query:
            yield MessageConnector(each)

    def add_users(self, users_id):
        # Adds users to a chat
        for id in set(users_id) - set(self.users_id):
            entry = Connector()
            entry.user_id = id
            entry.dial_id = self.id
            session.add(entry)
        session.commit()

    def delete_users(self, users_id):
        # Deletes user from a chat
        q = session.query(Connector)
        q.filter(Connector.dial_id ==
                 self.id, Connector.user_id.in_(users_id)).delete()
        session.commit()
