from flask_restful import reqparse, Resource
from flask import jsonify, session
import sys
from .db_funcs import UserConnector

class AuthResource(Resource):
    # Log in
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        try:
            user = UserConnector.login(args['login'], args['password'])
            if user is not None:
                session['logged_in'] = user.id
                return ({'status': "OK", 'uid': user.id}, 200)
            else:
                return ({'status': "ER", 'reason': 'wrong password'}, 401)
        except:
            return ({'status': "ER", 'reason': 'user not found'}, 404)
    # Sign up
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', required=True)
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        try: 
            uid = UserConnector.new_user(args['login'], args['email'], args['password']).id
            session['logged_in'] = uid
            return ({'status': "OK", 'uid': uid}, 200)
        except BaseException as e:
            return ({'status': "ER", 'reason': 'login or email is already taken'}, 409)