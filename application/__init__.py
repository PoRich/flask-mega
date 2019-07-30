from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.create_all()  # created through database migrations-TBC
mail = Mail(app)
login = LoginManager(app)
login.login_view = 'login'
# registers login function/endpoint with flask_login
login.login_message = _l('Please log in to access this page')
# override default login message so to enable translation
bootstrap = Bootstrap(app)
# https://pythonhosted.org/Flask-Bootstrap/basic-usage.html#available-blocks
moment = Moment(app)
babel = Babel(app)

from application import routes, models, errors


#  ERROR HANDLING
'''
note: emailing error logs from gmail requires changing security settings,
allowing for less secure apps
https://support.google.com/accounts/answer/6010255?hl=en
'''
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)  # reports only errors, not warnings
        app.logger.addHandler(mail_handler)  # attach to flask's logger object
        print('email sent')
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                        backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO) # DEBUG, INFO, WARNING, ERROR, CRITICAL
    app.logger.info('Microblog startup')


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])
    #return 'es'
