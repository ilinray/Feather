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


def hashed_password(password):
    return pbkdf2_hmac('sha512', bytes(password, 'u8'), bytes('bytes', 'u8'), 10)


def check_password(password, user_id):
    session = create_session()
    return session.query(User).get(user_id).hashed_password == hashed_password(password)


class BaseConnector:
    table = None
    table_attrs = set()
    def __init__(self, entry):
        self.id = entry.id
        self.entry = entry
    
    @classmethod
    def from_id(cls, id):
        try:
            return cls(session.query(cls.table).get(id))
        except:
            return None

    @classmethod
    def new(cls, table_attrs=None, **kwargs):
        entry = cls.table()
        if table_attrs is None:
            table_attrs = cls.table_attrs
        foo = table_attrs - set(kwargs.keys())
        if foo:
            raise TypeError(f'Wrong args. Not found: {str(foo)}')
        for k in table_attrs:
            setattr(entry, k, kwargs[k])
        session.add(entry)
        session.commit()
        return cls(entry)


class MessageConnector(BaseConnector):
    table = Message
    table_attrs = set(('text',
                       'user_id',
                       'created_date',
                       'dialog_id'))
    @classmethod
    def new(cls, files=[], **kwargs):
        msg = super().new(table_attrs=cls.table_attrs, **kwargs)
        for f in files:
            FileConnector.register_file(kwargs['dialog_id'], f, msg.id)
        return msg
    
    def to_dict(self):
        files = []
        for file in self.entry.files:
            d = {'filename': file.filename,
                 'file_id': f'{file.file_access}_{file.id}'}
            d.append(files)
        retval = {'id': self.id,
                  'text': self.entry.text,
                  'uid': self.entry.user_id,
                  'datetime': self.entry.created_date.isoformat(timespec='seconds'),
                  'files': files}
        return retval

    def delete(self):
        session.query(Message).filter(Message.id == self.id).delete()


class FileConnector(BaseConnector):
    table = File
    table_attrs = set(('filename',
                       'message_id',
                       'file_access'))

    @classmethod
    def register_file(cls, access, file, message_id):
        id = cls.new(filename=file.filename, message_id=message_id, file_access=access).id
        new_filename = f'{access}_{id}'
        file.save('user_imgs/' + new_filename)


class UserConnector(BaseConnector):
    table = User
    table_attrs = set(('login',
                       'email',
                       'password'))

    @classmethod
    def new(cls, **kwargs):
        user = super().new(table_attrs=cls.table_attrs, **kwargs)
        user.entry.hashed_password = hashed_password(kwargs['password'])
        return user

    def check_password(self, password):
        return hashed_password(password) == self.entry.hashed_password

    @classmethod
    def login(cls, login, password):
        entry = session.query(User).filter(User.login == login).first()
        if entry is None:
            return None
        user = cls(entry)
        if user.check_password(password):
            return user
        else:
            raise ValueError
    
    def get_chats(self):
        for each in self.entry.dialogs:
            yield DialogConnector(each)
    
    @classmethod
    def exists_from_login(cls, login):
        return session.query(User).filter(User.login == login).first() is not None

    @classmethod
    def exists_from_id(cls, id):
        return session.query(User).get(id) is not None

class DialogConnector(BaseConnector):
    table = Dialog
    table_attrs = set(('host_id', 'name'))

    @classmethod
    def new(cls, **kwargs):
        if 'name' not in kwargs.keys():
            kwargs['name'] = 'Chat'
        dialog = super().new(table_attrs=cls.table_attrs, **kwargs)
        for id in kwargs['users_id']:
            entry = Connector()
            entry.user_id = id
            entry.dial_id = dialog.id
            session.add(entry)
        session.commit()
        return dialog

    def get_users(self):
        for each in self.entry.users:
            yield UserConnector(each)
    
    def get_users_id(self):
        for each in self.entry.users:
            yield each.id

    def get_messages(self, count, offset):
        for each in self.entry.messages.order_by(Message.id.desc()).offset(offset).limit(count):
            yield MessageConnector(each)

