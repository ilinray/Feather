from flask_restful import reqparse, Resource, request
from flask import jsonify, session
import sys
from .db_funcs import UserConnector, DialogConnector, MessageConnector
from datetime import datetime


class ChatsResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, required=True)
        args = parser.parse_args()
        uid = args['uid']
        if uid != session['logged_in']:
            return ({'status': 'ER', 'reason': 'you are not logged in'}, 401)
        info = []
        user = UserConnector.from_id(uid)
        if user is None:
            return ({'status': 'ER', 'reason': 'user not found'}, 404)
        for dial in user.get_chats():
            dial_info = {'picture': ('d' + str(dial.id) + '.jpeg') if dial.entry.has_pic else None}
            mp = len(list(dial.entry.users.all())) == 2
            if mp:
                dial_info['name'] = dial.entry.name
            else:
                a, b, *_ = dial.entry.users
                dial_info['name'] = b.login if a.id == uid else a.login
            info.append(dial_info)
        return {'status': 'OK', 'chats': info}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, required=True)
        parser.add_argument('name')
        args = parser.parse_args()
        uid = args['uid']
        users = request.json()['users_id']
        if uid not in users:
            users.append(uid)
        if uid != session['logged_in']:
            return ({'status': 'ER', 'reason': 'you are not logged in'}, 401)
        for uid_ in users:
            guest = UserConnector.from_id(uid_)
            if guest is None:
                return ({'status': 'ER', 'reason': 'user not found'}, 404)
        return {'status': 'OK',
                'id': DialogConnector.new(host_id=uid, name=args['name'], users_id=users).id}


class UserInfoResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, defaut=0)
        parser.add_argument('login', defaut='')
        parser.add_argument('exists', type=int, defaut=0)
        args = parser.parse_args()
        if args['exists']:
            if args['login']:
                f = UserConnector.exists_from_login(args['login'])
            elif args['uid']:
                f = UserConnector.exists_from_id(args['uid'])
            else:
                f = 0
            return '1' if f else '0'
        else:
            return ''



class MessageResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, required=True)
        parser.add_argument('dialog_id', type=int, required=True)
        parser.add_argument('offset', type=int, default=0)
        parser.add_argument('count', type=int, default=20)
        args = parser.parse_args()
        if args['uid'] != session['logged_in']:
            return ({'status': 'ER', 'reason': 'you are not logged in'}, 401)
        dial = DialogConnector.from_id(args['dialog_id'])
        if dial is None:
            return ({'status': 'ER', 'reason': 'dialog not found'}, 404)
        if args['uid'] not in dial.get_users_id():
            return ({'status': 'ER', 'reason': 'you are not in chat'}, 401)
        msgs = dial.get_messages(args['count'], args['offset'])
        return {'status': 'OK',
                'msgs': [m.to_dict() for m in msgs]}
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, required=True)
        parser.add_argument('dialog_id', type=int, required=True)
        args = parser.parse_args()
        uid = args['uid']
        did = args['dialog_id']
        if uid != session['logged_in']:
            return ({'status': 'ER', 'reason': 'you are not logged in'}, 401)
        dial = DialogConnector.from_id(int(did))
        if dial is None:
            return ({'status': 'ER', 'reason': 'dialog not found'}, 404)
        if uid not in (u.id for u in dial.get_users()):
            return({'status': 'ER', 'reason': 'You have no access to that dialog'}, 401)
        text = request.form['text']
        time = datetime.now()
        files = request.files.values()
        id = MessageConnector.new(user_id=uid, text=text, files=files,time=time, dialog_id=did).id
        return {'status': 'OK', 'id': id}

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, required=True)
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()
        uid = args['uid']
        mid = args['id']
        if uid != session['logged_in']:
            return ({'status': 'ER', 'reason': 'you are not logged in'}, 401)
        msg = MessageConnector.from_id(mid)
        if msg is None:
            return ({'status': 'ER', 'reason': 'message not found'}, 404)
        if msg.entry.user_id != uid:
            return ({'status': 'ER', 'reason': 'not your message'}, 401)
        msg.delete()
        return {'status': 'OK'}

    def patch(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, required=True)
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()
        uid = args['uid']
        mid = args['id']
        if uid != session['logged_in']:
            return ({'status': 'ER', 'reason': 'you are not logged in'}, 401)
        msg = MessageConnector.from_id(mid)
        if msg is None:
            return ({'status': 'ER', 'reason': 'message not found'}, 404)
        if msg.entry.user_id != uid:
            return ({'status': 'ER', 'reason': 'not your message'}, 401)
        msg.entry.text = request.form['text']
        return {'status': 'OK'}


class DialogResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, required=True)
        parser.add_argument('dialog_id', type=int, required=True)
        args = parser.parse_args()
        uid = args['uid']
        did = args['dialog_id']
        if uid != session['logged_in']:
            return ({'status': 'ER', 'reason': 'you are not logged in'}, 401)
        dial = DialogConnector.from_id(int(did))
        if dial is None:
            return ({'status': 'ER', 'reason': 'dialog not found'}, 404)
        if uid not in (u.id for u in dial.get_users()):
            return({'status': 'ER', 'reason': 'You have no access to that dialog'}, 401)
        