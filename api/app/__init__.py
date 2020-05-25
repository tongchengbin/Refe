from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import config
from app.host import bp_host
from app.sys import bp_sys
import db
from core.flask_override import JsonResponse
from flask_cors import CORS


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    CORS(app, resources=r"/*")  # 设置跨域
    app.response_class = JsonResponse
    app.register_blueprint(bp_host, url_prefix="/host")
    app.register_blueprint(bp_sys, url_prefix="/sys")
    app.errorhandler(Exception)
    config[config_name].init_app(app)
    db.init_app(app)
    return app
