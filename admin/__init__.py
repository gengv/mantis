#coding: utf-8

from contextlib import contextmanager
from database import db_session, get_scoped_db_session
from exception import DataNotFoundException, InvalidOperationException
from flask import request, session, redirect, url_for
from flask.blueprints import Blueprint
from intercepter import template
from model import ArticleCatalog, Article, ArticleContent, \
    association_table_catalog_article, ArticleReply, User
from security import _get_current_user_id
from security.permissions import normal_user_permission
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.functions import func
import datetime
import math
import re

mod = Blueprint('admin', __name__, static_folder='static', template_folder='templates')


@mod.errorhandler(DataNotFoundException)
@template("error_page.html")
def handle_data_not_found_exception(e):
    return {'_result': False, 'error_message': e.message}


@mod.route('/article/new/')
@normal_user_permission.require()
@template(name='article_edit.html')
def create_article():
    _author_id = _get_current_user_id()
    _catalogs = _list_catalogs(_author_id)
    
    return {
            'author_id': _author_id,
            'catalog_list': _catalogs,
            }
    
    
@mod.route('/article/edit/<int:_article_id>')
@normal_user_permission.require()
@template(name='article_edit.html')
def edit_article(_article_id):
    _article = _read_article(_article_id)
    
    _author_id = _get_current_user_id()
    _catalogs = _list_catalogs(_author_id)
                                                
    return {
            'author_id': _author_id,
            'article': _article, 
            'article_catalogs': [_ac.id for _ac in _article.catalogs], 
            'catalog_list': _catalogs}


def _read_article(_article_id):
    with get_scoped_db_session(False) as _dbss:
        _article = _dbss.query(Article).options(joinedload(Article.content),
                                                joinedload(Article.author),
                                                joinedload(Article.catalogs),
                                                joinedload(Article.keywords)).get(_article_id)
                                                
        if _article:
            return _article
        else:
            raise DataNotFoundException('未能找到相应的文章！')
    

@mod.route('/article/save/', methods=['POST'])
@normal_user_permission.require()
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
        # 如果_id为空，则表示是新创建文章
        if not _id:
            _article = Article()
            _article.published_datetime = _now
            _article.content = ArticleContent()
        
        # 否则，表示修改文章    
        else:
            _id = int(_id)
            
            try:
                _article = _dbss.query(Article).options(load_only(Article.id)).filter_by(id=_id, author_id=_author_id).one()
            except NoResultFound:
                raise DataNotFoundException('未能找到要保存的文章！')
            
             
        _article.title = _title
        _article.author_id = _author_id
        _article.digest = _digest if _digest else (_content[:30] if len(_content)>30 else _content)
        _article.content.content = _content,
        _article.last_modified_datetime = _now
         
        if not _id:
            # 持久化存入文章
            _dbss.add(_article)
            _dbss.flush()
        else:
            # 删除文章与目录的关系
            _dbss.execute(association_table_catalog_article.delete()\
                                                           .where(association_table_catalog_article.c.article_id==_article.id))  # @UndefinedVariable
        
        # 新建（重建）文章与目录的关系
        for _cid in _catalogs:
            _cid = int(_cid)
            _dbss.execute(association_table_catalog_article.insert().values({
                                                                             'catalog_id': _cid,
                                                                             'article_id': _article.id,
                                                                             }))
    
        return redirect(url_for("blog.view_article", _article_id=_article.id))


@mod.route('/article/remove/', methods=['POST'])
@template()
def remove_article():
    _article_id = request.form['article_id']
    
    with get_scoped_db_session() as _dbss:
        # 检查当前用户是否为文章作者
        _author_id = _dbss.query(Article.author_id).get(_article_id).scalar()
        
        if _author_id == _get_current_user_id():
            _dbss.query(Article).filter_by(id=_article_id).update({'state': Article.HIDDEN})
            
            return [True, _article_id]
            
        else:
            raise InvalidOperationException("不能移除他人的文章！")
        

@mod.route('/article/delete/', methods=['POST'])
@template()
def delete_article():
    _article_id = request.form['article_id']

    with get_scoped_db_session() as _dbss:
        # 检查当前用户是否为文章作者
        _author_id = _dbss.query(Article.author_id).filter(Article.id==_article_id).scalar()
        
        if _author_id == _get_current_user_id():
            # 解除Article与Catalog之间的关联关系
            _dbss.execute(association_table_catalog_article.delete()
                                                           .where(association_table_catalog_article.c.article_id==_article_id))  # @UndefinedVariable
            # 删除Article记录
            _dbss.query(Article).filter_by(id=_article_id).delete()
            
            return {'_result': True, }
            
        else:
            raise InvalidOperationException('不能删除他人的文章！')
    


@mod.route('/reply/delete/', methods=['POST'])
@template()
def delete_reply():
    _reply_id = request.form['reply_id']
    
    with get_scoped_db_session(False) as _dbss:
        _article_author_id = _dbss.query(Article.author_id).join(ArticleReply).filter(ArticleReply.id==_reply_id).scalar()
        
        if _article_author_id == _get_current_user_id():
            _dbss.query(ArticleReply).filter_by(id=_reply_id).delete()
        
            return {'_result': True, }
        
        else:
            raise InvalidOperationException('不能删除他人文章的评论！')


def _list_catalogs(_owner_id):
    with get_scoped_db_session(False) as _dbss:
        _catalogs = _dbss.query(ArticleCatalog).filter_by(owner_id=_owner_id).all()
        return _catalogs
    

@mod.route('/catalog/new/', methods=['POST'])
@template()
def create_catalog():
    _name = request.form['catalog_name']
    
    _new_catalog = ArticleCatalog(name=_name)
    
    with get_scoped_db_session() as _dbss:
        _count = _dbss.query(func.count(ArticleCatalog.id)).filter(ArticleCatalog.name==_name).scalar()
        
        if _count > 0:
            raise InvalidOperationException('已经存在同名的分类目录！')
        else:
            _dbss.add(_new_catalog)
            _dbss.flush()
    
            return {'_result': True, 'new_catalog_id': _new_catalog.id}


@mod.route('/catalog/edit/', methods=['POST'])
@template()
def edit_catalog():
    _id, _name = request.form['id'], request.form['name']    
        
    with get_scoped_db_session() as _dbss:
        _count = _dbss.query(func.count(ArticleCatalog.id)).filter(ArticleCatalog=_name).scalar()
        
        if _count > 0:
            raise InvalidOperationException('已经存在同名的分类目录！')
        else:
            _dbss.query(ArticleCatalog).filter_by(id=_id).update({'name':_name})
    
            return {'_result': True, }


@mod.route('/catalog/delete/', methods=['POST'])
@template()
def delete_catalog():
    _id = request.form['id']
    
    with get_scoped_db_session() as _dbss:
        _dbss.execute(association_table_catalog_article.delete()
                                                       .where(association_table_catalog_article.c.catalog_id==_id))  # @UndefinedVariable
        _dbss.query(ArticleCatalog).filter_by(id=_id).delete()
    
        return {'_result': True, }


