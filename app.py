# coding: utf-8
from flask.app import Flask
from flask.globals import session
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed
import public
import blog
import security


app = Flask(__name__)

# 设置secret_key
app.secret_key = 'Z+9hn1d+yz'

# 设置Principal
principals = Principal(app)

# 设置身份验证回调
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    if session.has_key('_user'):
        _user = session['_user']
     
        identity.provides.add(UserNeed(_user['id']))
        
        for r in _user['role_ids']:
            identity.provides.add(RoleNeed(r))


# 设置Blueprint
app.register_blueprint(blog.mod, url_prefix='/blog')
# app.register_blueprint(admin.mod, url_prefix='/admin')
app.register_blueprint(security.mod, url_prefix='/security')
app.register_blueprint(public.mod, url_prefix='/public')

@app.teardown_appcontext
def shutdown_db_session(exception=None):
    from database import db_session
    db_session.remove()
    
    
@app.template_filter('strftime')
def filter_strftime(_datetime):
    return _datetime.strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    app.run(debug=True)