from flask_restful import reqparse, Resource
from flask import jsonify
import sys
from .db_funcs import UserConnector, DialogConnector


def dialogs_resources(app):
    class ChatsResource(Resource):
        def get(self):
            parser = reqparse.RequestParser()
            parser.add_argument('uid', required=True)
            args = parser.parse_args()
            