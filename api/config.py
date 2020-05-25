import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bingo'
    DATABASE = {
        "host": "192.168.66.128",
        "port": 3306,
        "passwd": "123",
        "user": "root",
        "db": "refe",
        "charset": "utf8"

    }
    CACHE_CONFIG = {
        'host': '127.0.0.1',
        'port': 6379,
        'password': '',
        'db': 0
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}