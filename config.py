import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        b'\x15(\x14\x1c\xf2\xc7i\xa7(\xcf\t-\xd1*\x11\xf7'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://federer:grandestslam@localhost:5432/flaskmega'
    # 'sqlite:///' + os.path.join(basedir,'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = \
        os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') or \
        False

    POSTS_PER_PAGE = 3

    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY') or \
        'e5ec5b69911f46e4aefe6caa3271a69f'


    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['bedfordap1@gmail.com']
    # list of emails to receive error reports


class DevelopmentConfig(Config):
    # NOT IN USE - need to configure app factory to use APP_SETTINGS
    ENV = 'development'
    DEBUG = 1

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')


class ProductionConfig(Config):
    # NOT IN USE - need to configure app factory to use APP_SETTINGS
    ENV = 'production'

    DEBUG = 0
    DEVELOPMENT = 0
    LOG_TO_STDOUT = 1

    DATABASE_URL = 'postgres://ijukbfnwqsckxp:5f35e6f8e73079f1e7b6a9799b12cf2935183f8f90ac4b9b286bc5b5935d3b61@ec2-50-16-225-96.compute-1.amazonaws.com:5432/d5vvard2u9haa3'
    ELASTICSEARCH_URL = 'https://paas:9b63e550a6ea0bf4ada40ffb1a5cb59a@thorin-us-east-1.searchly.com'

    WEB_CONCURRENCY = 2

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = int(586)
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'bedfordap1@gmail.com'
    MAIL_PASSWORD = 'vXjWhfwTpo+N3'
