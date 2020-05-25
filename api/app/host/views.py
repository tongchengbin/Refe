from flask import Response

from . import bp_host


@bp_host.route('/index', methods=['GET', 'POST'])
def index():
    return Response("Ok",500)