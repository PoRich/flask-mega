from flask import g
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth
from application.models import User
from application.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password  # register required Flask-HTTPAuth functions
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user  # allows access from the API view functions
    return user.check_password(password)


@basic_auth.error_handler  # register required Flask-HTTPAuth functions
def basic_auth_error():
    return error_response(401)


@token_auth.verify_token  # register required Flask-HTTPAuth functions
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None


@token_auth.error_handler  # register required Flask-HTTPAuth functions
def token_auth_error():
    return error_response(401)
