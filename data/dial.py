from flask_restful import reqparse, Resource, request
from flask import jsonify, session
import sys
from .db_funcs import UserConnector, DialogConnector, MessageConnector
from datetime import datetime
from .validators import *


@check(user_exists, correct_uid)
class ChatsResource(Resource):
    def get(self, uid):
        info = []
        user = UserConnector.from_id(uid)
        for dial in user.chats:
            mp = len(list(dial.users_id)) != 2
            if mp:
                dial_info = {'picture': f'-2_{dial.id}' if dial.entry.has_pic else None}
                dial_info['name'] = dial.entry.name
            else:
                a, b, *_ = dial.users
                enemy = b if a.user_id == uid else a
                dial_info = {'picture': f'-1_{enemy.id}' if enemy.has_pic else None}
                dial_info['name'] = enemy.login
            info.append(dial_info)
        return {'status': 'OK', 'chats': info}, 200

    def post(self, uid):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()
        users = request.json['users_id']
        if uid not in users:
            users.append(uid)
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
        login = args['login']
        uid = args['uid']
        if args['exists']:
            if login:
                f = UserConnector.exists_from_login(login)
            elif args['uid']:
                f = UserConnector.exists_from_id(uid)
            else:
                f = 0
            return '1' if f else '0'
        else:
            if login:
                UserConnector.from_login()

    @check(user_exists, correct_uid)
    def post(self, uid):
        request.files.values()[0].save(f'user_imgs/-1_{uid}')
        return {'status': 'OK'}, 200


class MessageResource(Resource):
    @check(user_exists, correct_uid, dialog_exists, dialog_belongs_to_user)
    def get(self, uid, dial, dialog_id):
        parser = reqparse.RequestParser()
        parser.add_argument('offset', type=int, default=0)
        parser.add_argument('count', type=int, default=20)
        args = parser.parse_args()
        msgs = dial.get_messages(args['count'], args['offset'])
        return {'status': 'OK',
                'msgs': [m.to_dict() for m in msgs]}

    @check(user_exists, correct_uid, dialog_exists, dialog_belongs_to_user)
    def post(self, uid, dial, dialog_id):
        text = request.form['text']
        time = datetime.now()
        files = request.files.values()
        id = MessageConnector.new(user_id=uid, text=text, files=files,time=time, dialog_id=dialog_id).id
        return {'status': 'OK', 'id': id}

    @check(user_exists, correct_uid)
    def delete(self, uid):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()
        mid = args['id']
        msg = MessageConnector.from_id(mid)
        if msg is None:
            return ({'status': 'ER', 'reason': 'message not found'}, 404)
        if msg.entry.user_id != uid:
            return ({'status': 'ER', 'reason': 'not your message'}, 401)
        msg.delete()
        return {'status': 'OK'}

    @check(user_exists, correct_uid)
    def patch(self, uid):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()
        mid = args['id']
        msg = MessageConnector.from_id(mid)
        if msg is None:
            return ({'status': 'ER', 'reason': 'message not found'}, 404)
        if msg.entry.user_id != uid:
            return ({'status': 'ER', 'reason': 'not your message'}, 401)
        msg.entry.text = request.form['text']
        return {'status': 'OK'}


@check(user_exists, correct_uid, dialog_exists, dialog_belongs_to_user)
class DialogResource(Resource):
    def get(self, uid, dialog_id, dial):
        info = {'id': dial.id,
                'pic': f'-2_{dial.id}' if dial.entry.has_pic else None,
                'name': dial.entry.name,
                'users_id': list(dial.users_id)}
        return {'status': 'OK', 'info': info}, 200

    def post(self, uid, dialog_id, dial):
        users = request.json['users_id']
        for guest_uid in users:
            if not UserConnector.exists_from_id(guest_uid):
                return {'status': 'ER', 'reason': f'user {guest_uid} not found'}, 404
        dial.add_users(users)
        return {'status': 'OK'}, 200