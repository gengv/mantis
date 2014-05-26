# coding: utf-8
from database import db_session
from model import ArticleCatalog
import random

def _test_create_catalog():
    _name = 'Test_ArticleCatalog_%s' % random.randint(100001, 999999)
    _new_catalog = ArticleCatalog(name=_name)
    
    db_session.add(_new_catalog)  # @UndefinedVariable
    db_session.commit()  # @UndefinedVariable
    
    
def _test_edit_catalog():
    _catalog = db_session.query(ArticleCatalog).get(random.randint(1, 20))  # @UndefinedVariable
    
    _new_name = 'Test_ArticleCatalog_%s' % random.randint(100001, 999999)
    _id, _old_name, _catalog.name = _catalog.id, _catalog.name, _new_name
        
    db_session.commit()  # @UndefinedVariable
    print 'Catalog [%s] renamed from [%s] to [%s]' % (_id, _old_name, _new_name)
    
def _test_edit_catalog_2():
    _cid = random.randint(1, 20)
    _new_name = 'Test_ArticleCatalog_%s' % random.randint(100001, 999999)
    
    db_session.query(ArticleCatalog).filter_by(id=_cid).update({'name':_new_name})  # @UndefinedVariable
    db_session.commit()  # @UndefinedVariable
    print 'Catalog [%s] renamed to [%s]' % (_cid, _new_name)
    
if __name__ == '__main__':
    for i in range(20):
        _test_create_catalog()
        
    _test_edit_catalog_2()