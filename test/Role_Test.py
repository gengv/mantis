# coding: utf-8
from database import get_scoped_db_session
from model import Role, User
from random import randint

if __name__ == '__main__':
    _role = Role()
    _role.name = 'Normal User'
    
    with get_scoped_db_session() as _dbss:
        for i in range(20):
            _u = _dbss.query(User).get(i+1)
            _role.users.append(_u)
            
        _dbss.add(_u)