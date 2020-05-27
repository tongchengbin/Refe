# 主机管理
from flask import Blueprint
bp_host = Blueprint('host', __name__)
from . import views
bp_host.add_url_rule('/type', view_func=views.HostTypeView.as_view('host_type'))
bp_host.add_url_rule('/', view_func=views.HostView.as_view('host'))