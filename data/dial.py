from flask_restful import reqparse, Resource
from flask import jsonify
import sys
from .db_funcs import UserConnector, DialogConnector


def chats_resource(app):
    class ChatsResource(Resource):
        def get(self):
            parser = reqparse.RequestParser()
            parser.add_argument('uid', required=True)
            args = parser.parse_args()
            if args['uid'] != app.session['logged_in']:
                return jsonify({})