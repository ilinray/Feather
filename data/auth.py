from flask_restful import reqparse, abort, Resource
from flask import jsonify, abort
import sys
from .db_funcs import UserConnector


def auth_resource(app):
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
                    app.session['logged_in'] = user.id
                    return jsonify({'status': "OK",
                                    'uid': user.id})
                else:
                    return jsonify({'status': "ER"}), 401
            except:
                return jsonify({'status': "ER"}), 404

        # Sign up
        def post(self):
            parser = reqparse.RequestParser()
            parser.add_argument('login', required=True)
            parser.add_argument('email', required=True)
            parser.add_argument('password', required=True)
            args = parser.parse_args()
            uid = UserConnector.new_user(args['login'], args['email'], args['password']).id
            app.session['logged_in'] = uid
            return jsonify({'status': "OK", 'uid': uid})
