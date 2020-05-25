# 主机管理
from flask import Blueprint
bp_host = Blueprint('host', __name__)
from . import views
