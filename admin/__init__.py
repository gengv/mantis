#coding: utf-8

from contextlib import contextmanager
from database import db_session, get_scoped_db_session
from flask import request, session, redirect, url_for
from flask.blueprints import Blueprint
from intercepter import template
from model import ArticleCatalog, Article, ArticleContent, \
    association_table_catalog_article, ArticleReply, User
from security import _get_current_user_id
from security.permissions import normal_user_permission
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.functions import func
import datetime
import math
import re

mod = Blueprint('admin', __name__, static_folder='static', template_folder='templates')


@mod.route('/article_list/', defaults={'_catalog_id': 0})
@mod.route('/article_list/<int:_catalog_id>')
@template('article_list.html')
def list_articles(_catalog_id, _page_no):
    _author_id = _get_current_user_id()
    
    _size_per_page = 10
    
    # 查询文章数量
    _count_of_articles = _count_articles(_author_id, _catalog_id)
    # 计算最大页数
    _max_page_no = int(math.ceil((1.0*_count_of_articles/_size_per_page)))
    # 如果当前页超过最大页数，则使用最大页数
    if _page_no > _max_page_no: _page_no = _max_page_no
    # 计算查询的偏移量
    _offset = (_page_no-1) * _size_per_page
    
    # 查询实体对象
    _catalogs = _list_catalogs(_author_id)
    _articles = _list_articles_basic(_author_id=_author_id, _catalog_id=_catalog_id, _offset=_offset, _size=_size_per_page)
    
    # 查询文章的Reply数
    _reply_counts = _count_replies_by_articles([_a.id for _a in _articles])
    for _a in _articles:
        _a.reply_count = _reply_counts[_a.id]
    
    return {
            'articles': _articles, 
            'catalogs':_catalogs, 
            'current_page_no':_page_no,
            'max_page_no': _max_page_no,
            'prefix_url': _remove_page_from_url(request.base_url)
            }
    
    
def _count_articles(_author_id, _catalog_id=None):
    with get_scoped_db_session(False) as _dbss:
        _query = _dbss.query(func.count(Article.id))\
                                     
        if _catalog_id:
            _query = _query.join(Article.catalogs).filter(Article.author_id==_author_id)\
                                                  .filter(ArticleCatalog.id==_catalog_id)
        else:
            _query = _query.filter(Article.author_id==_author_id)
            
        _count = _query.scalar()
            
        return _count
    

def _list_articles_basic(_author_id, _catalog_id=None, _offset=1, _size=10):
    with get_scoped_db_session(False) as _dbss:
        _query = _dbss.query(Article).join(Article.catalogs)\
                                     .filter(Article.author_id==_author_id)
        if _catalog_id:
            _query = _dbss.query(Article).join(Article.catalogs)\
                                         .filter(Article.author_id==_author_id)\
                                         .filter(ArticleCatalog.id==_catalog_id)
                                         
        else:
            _query = _dbss.query(Article).filter_by(author_id=_author_id)
            
        _articles = _query.order_by(Article.published_datetime)[_offset:_offset+_size]
        return _articles
    
    
def _count_replies_by_articles(_article_ids):
    if _article_ids is None:
        _article_ids = []
    
    with get_scoped_db_session(False) as _dbss:
        _result_set = _dbss.query(ArticleReply.article_id, func.count(ArticleReply.id))\
                           .filter(ArticleReply.article_id.in_(_article_ids))\
                           .group_by(ArticleReply.article_id).all()
        
        return dict(_result_set)
    

def _remove_page_from_url(_url):
    _p = re.compile(r'(.*)/p/\d*$')
    _m = re.match(_p, _url)
    
    if _m:
        return _m.group(1)
    else:
        return _url


@mod.route('/article/new/')
@normal_user_permission.require()
@template(name='article_edit.html')
def create_article():
    _author_id = _get_current_user_id()
    _catalogs = _list_catalogs(_author_id)
    
    return {'catalog_list': _catalogs}
    
    
@mod.route('/article/view/<int:_article_id>')
@template(name='article.html')
def view_article(_article_id):
    _article = _read_article(_article_id)
    
    _author_id = _get_current_user_id()
    _catalogs = _list_catalogs(_author_id)
                                                
    return {'article': _article, 'catalogs': _catalogs}


@mod.route('/article/edit/<int:_article_id>')
@normal_user_permission.require()
@template(name='article_edit.html')
def edit_article(_article_id):
    _article = _read_article(_article_id)
    
    _author_id = _get_current_user_id()
    _catalogs = _list_catalogs(_author_id)
                                                
    return {'article': _article, 
            'article_catalogs': [_ac.id for _ac in _article.catalogs], 
            'catalog_list': _catalogs}


def _read_article(_article_id):
    with get_scoped_db_session(False) as _dbss:
        _article = _dbss.query(Article).options(joinedload(Article.content),
                                                joinedload(Article.author),
                                                joinedload(Article.catalogs),
                                                joinedload(Article.keywords)).get(_article_id)
                                                
        return _article
    

@mod.route('/article/save/', methods=['POST'])
@normal_user_permission.require()
@template()
def save_article():
    _author_id = _get_current_user_id()
    
    _id, _title, _digest, _content, _catalogs = \
        request.form.get('id'), \
        request.form.get('title'), \
        request.form.get('digest'), \
        request.form.get('content'), \
        request.form.getlist('catalog_id')
        
    _now = datetime.datetime.now()
        
    with get_scoped_db_session() as _dbss:
        if not _id:
            _article = Article()
            _article.published_datetime = _now
            _article.content = ArticleContent()
            
        else:
            _id = int(_id)
            _article = _dbss.query(Article).options(load_only(Article.id)).filter_by(id=_id, author_id=_author_id).one()
             
        _article.title = _title
        _article.author_id = _author_id
        _article.digest = _digest,
        _article.content.content = _content,
        _article.last_modified_datetime = _now
         
        if not _id:
            _dbss.add(_article)
            _dbss.flush()
        else:
            _dbss.execute(association_table_catalog_article.delete()\
                                                           .where(association_table_catalog_article.c.article_id==_article.id))  # @UndefinedVariable
             
        for _cid in _catalogs:
            _cid = int(_cid)
            _dbss.execute(association_table_catalog_article.insert().values({
                                                                             'catalog_id': _cid,
                                                                             'article_id': _article.id,
                                                                             }))
    
        return [True, _article.id]


@mod.route('/article/remove/', methods=['POST'])
@template()
def remove_article():
    _id = request.form['id']
    
    with get_scoped_db_session() as _dbss:
        _dbss.query(Article).filter_by(id=_id).update({'state': Article.HIDDEN})
        
    return 'Article removed [%s]' % _id


@mod.route('/article/remove_batch/', methods=['POST'])
@template()
def remove_article_batch():
    _ids = request.form.getlist('id')
    
    with get_scoped_db_session() as _dbss:
        for _id in _ids:
            _dbss.query(Article).filter_by(id=_id).update({'state': Article.HIDDEN})
        
    return 'Article batch removed [%s]' % (','.join([str(_id) for _id in _ids]))


@mod.route('/article/delete/', methods=['POST'])
@template()
def delete_article():
    _id = request.form['id']

    with get_scoped_db_session() as _dbss:
        _dbss.execute(association_table_catalog_article.delete()
                                                       .where(association_table_catalog_article.c.article_id==_id))  # @UndefinedVariable
        _dbss.query(Article).filter_by(id=_id).delete()
    
    return 'Article deleted [%s]' % _id


@mod.route('/reply/delete/', methods=['POST'])
@template()
def delete_reply():
    _reply_id = request.form['reply_id']
    
    with get_scoped_db_session(False) as _dbss:
        _article_author_id = _dbss.query(Article.author_id).join(ArticleReply).filter(ArticleReply.id==_reply_id).scalar()
        
        if _article_author_id == _get_current_user_id():
            _dbss.query(ArticleReply).filter_by(id=_reply_id).delete()
        
            return [True, _reply_id]


def _list_catalogs(_owner_id):
    with get_scoped_db_session(False) as _dbss:
        _catalogs = _dbss.query(ArticleCatalog).filter_by(owner_id=_owner_id).all()
        return _catalogs
    

@mod.route('/catalog/new/', methods=['POST', 'GET'])
@template()
def create_catalog():
    if request.method == 'POST':
        _name = request.form['name']
    else:
        _name = request.args.get('name')
    
    _new_catalog = ArticleCatalog(name=_name)
    
    with get_scoped_db_session() as _dbss:
        _dbss.add(_new_catalog)
    
    return 'ArticleCatalog created [%s][%s]' % (_new_catalog.id, _new_catalog.name)


@mod.route('/catalog/new/', methods=['POST', 'GET'])
@template()
def edit_catalog():
    if request.method == 'POST':
        _id, _name = request.form['id'], request.form['name']
    else:
        _id, _name = request.args.get('id'), request.args.get('name')
        
    with get_scoped_db_session() as _dbss:
        _dbss.query(ArticleCatalog).filter_by(id=_id).update({'name':_name})
    
    return 'ArticleCatalog renamed [%s][%s]' % (_id, _name)


@mod.route('/catalog/delete/', methods=['POST', 'GET'])
@template()
def delete_catalog():
    if request.method == 'POST':
        _id = request.form['id']
    else:
        _id = request.args.get('id')
    
    with get_scoped_db_session() as _dbss:
        _dbss.execute(association_table_catalog_article.delete()
                                                       .where(association_table_catalog_article.c.catalog_id==_id))  # @UndefinedVariable
        _dbss.query(ArticleCatalog).filter_by(id=_id).delete()
    
    return 'ArticleCatalog deleted [%s]' % (_id, )


