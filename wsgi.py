from application import create_app, db, cli
from application.models import User, Post, Message, Notification, Task
# simply importing causes command decorators to run and regisrs the commands
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)
cli.register(app)

@app.shell_context_processor  # registers function as shell context function
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Message': Message,
            'Notification': Notification, 'Task': Task}
