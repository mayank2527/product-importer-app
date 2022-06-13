from flask import make_response, jsonify
from flask_restful import Resource


class Index(Resource):
    def get(self):
        return make_response(jsonify({"version": "v1"}), 200)
