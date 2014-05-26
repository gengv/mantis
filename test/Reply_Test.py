# coding: utf-8
from database import db_session, get_scoped_db_session
from hashlib import md5, sha224
from model import Article, ArticleContent, association_table_catalog_article, \
    User, ArticleReply
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import joinedload, undefer
import datetime
import random
import time


def test_create_reply():
    _author_id = random.randint(1, 20)
    _article_id = random.randint(1, 200)
    _reply = ArticleReply()
    _reply.article_id = _article_id
    _reply.author_id = _author_id
    
    _random_seed = str(random.random())
    _reply.content = 'reply content - %s' % (''.join(random.randint(10, 50)*sha224(_random_seed).hexdigest()))
    
    _reply.published_datetime = datetime.datetime.now()
    time.sleep(0.3)
    
    _dbss = db_session()
    _dbss.add(_reply)
    _dbss.commit()
    

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
        _articles = _dbss.query(Article).filter_by(author_id=_author_id).filter(Article.catalogs.any(id=_catalog_id)).all()  # @UndefinedVariable
    
    print '%s articles found.' % len(_articles)
    for _a in _articles:    
        print '[%s] %s' % (_a.id, _a.title)
        

def _test_view_article(_id):
#     _id = random.randint(1, 50)
    with get_scoped_db_session(False) as _dbss:
        _article = _dbss.query(Article).options(joinedload(Article.content), joinedload(Article.author)).get(_id)
        
#         print type(_article)
#         print _article.__dict__
#         print dir(_article)
        
    return _article
        
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
    for i in range(500):
        _a = test_create_reply()
#     _d = sa_obj_to_dict([_a])
#     print _d
    