# coding: utf-8
from flask.app import Flask
import admin
import blog


app = Flask(__name__)


app.register_blueprint(blog.mod, url_prefix='/blog')
app.register_blueprint(admin.mod, url_prefix='/admin')


@app.teardown_appcontext
def shutdown_session(exception=None):
    from database import db_session
    db_session.remove()
    
    
@app.template_filter('strftime')
def filter_strftime(_datetime):
    return _datetime.strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    app.run(debug=True)