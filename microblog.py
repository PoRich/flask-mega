from application import create_app, db, cli
from application.models import User, Post
# simply importing causes command decorators to run and regisrs the commands
from config import ProductionConfig

app = create_app(ProductionConfig)
cli.register(app)

@app.shell_context_processor  # registers function as shell context function
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
