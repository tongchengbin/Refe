# 系统账户权限管理
from flask import Blueprint
bp_sys = Blueprint("sys", __name__)
from . import views
