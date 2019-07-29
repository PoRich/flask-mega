from application import app, db
from application.models import User, Post

@app.shell_context_processor # registers function as shell context function
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
