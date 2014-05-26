# coding: utf-8
from database import db_session
from model import User
import random

def _test_create_user():
    _name = 'Test_User_%s' % random.randint(100001, 999999)
    _new_user = User(name=_name, email='%s@mantis.org' % _name)
    
    db_session.add(_new_user)  # @UndefinedVariable
    db_session.commit()  # @UndefinedVariable
    
def _test_edit_user():
    _user = db_session.query(User).get(random.randint(1, 20))  # @UndefinedVariable
    
    _new_name = 'Test_User_%s' % random.randint(100001, 999999)
    _id, _old_name, _user.name, _user.email = _user.id, _user.name, _new_name, '%s@mantis.org' % _new_name
        
    db_session.commit()  # @UndefinedVariable
    print 'User [%s] renamed from [%s] to [%s]' % (_id, _old_name, _new_name)
    
if __name__ == '__main__':
    for i in range(20):
        _test_create_user()
        
    _test_edit_user()