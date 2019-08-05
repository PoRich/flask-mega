import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir,'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = \
        os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') or \
        False

    POSTS_PER_PAGE = 5

    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')


    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['info@bedfordap.com']
    # list of emails to receive error reports

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')


class DevelopmentConfig(Config):
    # NOT IN USE - need to configure app factory to use APP_SETTINGS
    ENV = 'development'
    DEBUG = 1


class ProductionConfig(Config):
    # NOT IN USE - need to configure app factory to use APP_SETTINGS
    ENV = 'production'
    DEBUG = 0
    LOG_TO_STDOUT = 1
    WEB_CONCURRENCY = 4
