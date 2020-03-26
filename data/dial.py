from flask_restful import reqparse, Resource
from flask import jsonify, session
import sys
from .db_funcs import UserConnector, DialogConnector


class ChatsResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int, required=True)
        args = parser.parse_args()
        uid = args['uid']
        if uid == session['logged_in']:
            info = []
            user = UserConnector.from_id(uid)
            if user is None:
                return ({'status': 'ER', 'reason': 'user not found'}, 404)
            for dial in user.get_chats():
                mp = dial.entry.many_people
                dial_info = {'many_people': mp,
                             'picture': (str(dial.id) + '.jpeg') if dial.entry.has_pic else None}
                if mp:
                    dial_info['name'] = dial.entry.name
                else:
                    a, b, *_ = dial.entry.users
                    dial_info['name'] = b.login if a.id == uid else a.login
                info.append(dial_info)
            return ({'status': 'OK', 'chats': info}, 200)
        else:
            return ({'status': 'ER', 'reason': 'you are not logged in'}, 401)

