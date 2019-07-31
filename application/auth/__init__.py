from flask import Blueprint

bp = Blueprint('auth', __name__)

from application.auth import email, forms, routes
# register auth email, forms, routes with blueprint
