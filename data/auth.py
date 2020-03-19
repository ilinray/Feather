from flask_restful import reqparse, abort, Resource
from flask import jsonify
import sys
from .db_funcs import UserConnector

class AuthResource(Resource):

    # Log in
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        return jsonify({'status': "ER"})

    # Sign up
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', required=True)
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        uid = UserConnector.new_user(args['login'], args['email'], args['password']).id
        return jsonify({'status': "OK", 'uid': uid})
