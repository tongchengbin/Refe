import os
from flask_script import Manager,Shell
from werkzeug.exceptions import HTTPException

from app import create_app
app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.errorhandler(404)
def handle_404_error(err_msg):
    return r'%s' % (str(err_msg)), 404


@app.errorhandler(500)
def handle_404_error(err_msg):
    return r'%s' % (str(err_msg)), 500


@app.errorhandler(HTTPException)
def handle_exception(e):
    print("ee",e)
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    # replace the body with JSON
    response = {
        "status": e.code,
        "error": e.name,
        "description": str(e.description),
    }
    return response


manager = Manager(app)

if __name__ == '__main__':
    manager.run()
