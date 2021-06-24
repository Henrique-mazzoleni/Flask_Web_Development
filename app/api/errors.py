from flask import  jsonify
from werkzeug.wrappers import response

def bad_request(message):
    response = jsonify('error': 'bad request', 'message', message)
    response.status_code = 400
    return response

def unauthorized(message):
    response = jsonify('error': 'unauthorized', 'message': message)
    response.status_code = 401
    return response

def forbiden(message):
    response = jsonify('error': 'forbiden', 'message': message)
    response.status_code = 403
    return response

def not_found(message):
    response = jsonify('error': 'not found', 'message': message)
    response.status_code = 404
    return response

def internal_server_error(message):
    response = jsonify('error': 'internal server error', 'message': message)
    response.status_code = 500
    return response