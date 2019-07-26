import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        b'\x15(\x14\x1c\xf2\xc7i\xa7(\xcf\t-\xd1*\x11\xf7'
