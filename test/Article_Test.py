# coding: utf-8
from database import db_session, get_scoped_db_session
from hashlib import md5, sha224
from model import Article, ArticleContent, association_table_catalog_article, \
    User, ArticleCatalog
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import joinedload, undefer, defer, load_only
from sqlalchemy.sql.functions import func
import datetime
import random


def test_create_article():
    _author_id = random.randint(1, 20)
    
    _new_article = Article()
    _new_article.title = 'Test_Article_%s' % random.randint(100001, 999999)
    _new_article.author_id = _author_id
    _new_article.published_datetime = _new_article.last_modified_datetime = datetime.datetime.now()
    
    _random_seed = str(random.random())
    _new_article.digest = 'digest - %s' % (''.join(random.randint(2, 5)*md5(_random_seed).hexdigest()))
    
    _content = ArticleContent(content='content - %s' % (''.join(random.randint(10, 50)*sha224(_random_seed).hexdigest())))
    _new_article.content = _content
    
    db_session.add(_new_article)  # @UndefinedVariable
    db_session.flush()  # @UndefinedVariable
    
    _catalogs = [
                 random.randint(1, 20),
                 random.randint(1, 20),
                 random.randint(1, 20),
                 ]
    for _cid in _catalogs:
        db_session.execute(association_table_catalog_article.insert().values({  # @UndefinedVariable
                                                                              'catalog_id': _cid,
                                                                              'article_id': _new_article.id,
                                                                              }))
    db_session.commit()  # @UndefinedVariable
    

def _test_delete_article():
    _id = 197
    _dbss = db_session()
    try:
        _dbss.execute(association_table_catalog_article.delete().where(association_table_catalog_article.c.article_id==_id))  # @UndefinedVariable
        _dbss.query(Article).filter_by(id=_id).delete()  # @UndefinedVariable
        _dbss.commit()  # @UndefinedVariable
    except:
        import sys
        print sys.exc_info()[1]
        _dbss.rollback()
    
    print 'Article deleted [%s]' % _id
    
    
def _test_list_article():
    _author_id = random.randint(1, 20)
    _catalog_id = random.randint(1, 20)
    
    print '_author_id', _author_id
    print '_catalog_id', _catalog_id
    
    with get_scoped_db_session(False) as _dbss:
        _count = _dbss.query(func.count(Article.id)).filter_by(author_id=_author_id).scalar()
#         _articles = _dbss.query(Article).options(joinedload(Article.catalogs)).filter_by(author_id=_author_id).all()
        _articles = _dbss.query(Article).join(Article.catalogs).filter_by(author_id=_author_id)\
                                            .filter(ArticleCatalog.id==_catalog_id).all()
#         _articles = _dbss.query(Article).filter_by(author_id=_author_id).filter(Article.catalogs.any(id=_catalog_id)).all()  # @UndefinedVariable
    
    print '%s articles found.' % _count
    for _a in _articles:    
        print '[%s] %s' % (_a.id, _a.title)#, [_c.name for _c in _a.catalogs]
        
        

def _test_view_article(_id):
#     _id = random.randint(1, 50)
    with get_scoped_db_session(False) as _dbss:
        _article = _dbss.query(Article).options(joinedload(Article.content), joinedload(Article.author)).get(_id)
        
#         print type(_article)
#         print _article.__dict__
#         print dir(_article)
        
    return _article

def _test_edit_article(_id):          
    with get_scoped_db_session() as _dbss:
        _article = _dbss.query(Article).options(load_only(Article.id)).filter_by(id=_id).one()
        _article.title = 'Test_Article_876987_CHANGED'
        _article.digest = 'digest - 121b57da464e57bd3c66976bb7483601121b57da464e57bd3c66976bb7483601_CHANGED',
        
        _article.content.content = 'content - _CHANGED_551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5551762938dc33954a326252612bb19eca5cd43eb478632f27b73aab5',
        _article.last_modified_datetime = datetime.datetime.now()
        
        _dbss.flush()
        
#         for _cid in _catalogs:
#             _dbss.execute(association_table_catalog_article.insert().values({
#                                                                              'catalog_id': _cid,
#                                                                              'article_id': _article.id,
#                                                                              }))
            
            
    
    return 'Article updated [%s][%s]' % (_article.id, _article.title)
        
#     print 'Article displayed [%s][%s][%s]' % (_article.id, _article.title, _article.author.name)
#     print _article.content.content


# def sa_obj_to_dict(obj):
#     if isinstance(obj.__class__, DeclarativeMeta):
#         _dict = {}
#         for _k, _v in obj.__dict__.iteritems():
#             if not _k.startswith('_'):
# #                 print _k, ': ', _v
#                 _v = sa_obj_to_dict(_v)
#                 _dict[_k] = _v
#             
#         return _dict
#     
#     elif type(obj)==list:
#         print '_list', obj
#         _list = []
#         for _item in obj:
#             _list.append(sa_obj_to_dict(_item))
#             
#         return _list
#     else:
#         return obj
    


    
    
     
if __name__ == '__main__':
#     for i in range(200):
#         test_create_article()
    
#     _test_delete_article()

#     _test_list_article()
    
#     _a = _test_view_article(5)
#     print _a, [_a]
#     _d = sa_obj_to_dict([_a])
#     print _d
    _test_edit_article(3)
    