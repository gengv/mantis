# coding: utf-8

from database import get_scoped_db_session
from flask.blueprints import Blueprint
from flask.globals import request, session, current_app
from flask_principal import identity_changed, Identity, AnonymousIdentity
from hashlib import md5
from intercepter import template
from model import User

mod = Blueprint('security', __name__, static_folder='static', template_folder='templates')

@mod.route('/login', methods=['POST'])
def login():
    _username = request.form['username']
    _password = request.form['password']
    
    with get_scoped_db_session() as _dbss:
#         try:
        _user = _dbss.query(User).filter(User.name==_username)\
                                 .filter(User.passcode==md5(_password).hexdigest()).one()
                                 
        _role_ids = [_r.id for _r in _user.roles]
        
        session['_user'] = {'id': _user.id, 
                            'name': _user.name,
                            'role_ids': _role_ids}
        
        identity_changed.send(current_app._get_current_object(), identity=Identity(_user.id))
            
#         except:
#             pass
        
        return 'Logged in!'
        
@mod.route('/logout')
def logout():
    for _k in ['identity.id', 'identity.auth_type', '_user']:
        session.pop(_k, None)
        
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    
    return 'Logged out!'
    
    
@mod.route('/login_form')
@template('login_form.html')
def login_form():
    return {}