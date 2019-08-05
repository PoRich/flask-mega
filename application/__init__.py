import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import current_app, Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from elasticsearch import Elasticsearch
from config import DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
migrate = Migrate()

login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page')
# registers login function/endpoint with flask_login
# override default login message so to enable translation
mail = Mail()
bootstrap = Bootstrap()
# https://pythonhosted.org/Flask-Bootstrap/basic-usage.html#available-blocks
moment = Moment()
babel = Babel()


def create_app(Config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # with app.app_context():
    #    db.create_all()

    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    from application.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from application.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from application.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/main')

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    #  ERROR HANDLING
    '''
    note: emailing error logs from gmail requires changing security settings,
    allowing for less secure apps
    https://support.google.com/accounts/answer/6010255?hl=en
    '''
    if not app.debug and not app.testing:
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
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log',
                                                maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s \
                [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO) # DEBUG, INFO, WARNING, ERROR, CRITICAL
            app.logger.info('Microblog startup')

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    #return 'es'
