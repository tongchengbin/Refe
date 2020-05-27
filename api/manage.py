import os

from flask_script import Manager,Shell

from app import create_app
app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.errorhandler(404)
def handle_404_error(err_msg):
    return r'%s' % (str(err_msg)), 404


@app.errorhandler(500)
def handle_404_error(err_msg):
    return r'%s' % (str(err_msg)), 500




manager = Manager(app)

print(app.url_map)
if __name__ == '__main__':
    manager.run()
