# coding: utf-8
from database import get_scoped_db_session
from exception import DataNotFoundException, InvalidOperationException
from flask import request, session, redirect, url_for
from flask.blueprints import Blueprint
from intercepter import template
from model import Article, ArticleCatalog, ArticleReply, User, ArticleContent, \
    association_table_catalog_article
from security import _get_current_user_id
from security.permissions import normal_user_permission
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.functions import func
import datetime
import math
import re

mod = Blueprint('blog', __name__, static_folder='static', template_folder='templates')


@mod.errorhandler(DataNotFoundException)
@template("error_page.html")
def handle_data_not_found_exception(e):
    return {'_result': False, 'error_message': e.message}


@mod.errorhandler(InvalidOperationException)
@template("error_page.html")
def handle_invalid_operation_exception(e):
    return {'_result': False, 'error_message': e.message}


@mod.route('/blog/<int:_author_id>', defaults={'_page_no': 1})
@mod.route('/blog/<int:_author_id>/p/<int:_page_no>')
@template(name='index.html')
def list_articles_by_author(_author_id, _page_no):
    _size_per_page = 5
    
    # 查询文章数量
    _count_of_articles = _count_articles(_author_id)
    # 计算最大页数
    _max_page_no = int(math.ceil((1.0*_count_of_articles/_size_per_page)))
    # 如果当前页超过最大页数，则使用最大页数
    if _page_no > _max_page_no: _page_no = _max_page_no
    # 计算查询的偏移量
    _offset = (_page_no-1) * _size_per_page
    
    # 查询实体对象
    _catalogs = _list_catalogs(_author_id)
    _articles = _list_articles_basic(_author_id=_author_id, _offset=_offset, _size=_size_per_page)
    
    # 查询文章的Reply数
    _reply_counts = _count_replies_by_articles([_a.id for _a in _articles])
    for _a in _articles:
        _a.reply_count = _reply_counts.get(_a.id, 0)
    
    return {
            'author_id': _author_id,
            'articles': _articles, 
            'catalogs':_catalogs, 
            'current_page_no':_page_no,
            'max_page_no': _max_page_no,
            'prefix_url': _remove_page_from_url(request.base_url),
            'editable': _author_id == _get_current_user_id(),
            }
    

@mod.route('/blog/<int:_author_id>/c/<int:_catalog_id>', defaults={'_page_no': 1})
@mod.route('/blog/<int:_author_id>/c/<int:_catalog_id>/p/<int:_page_no>')
@template(name='index.html')
def list_articles_by_author_and_category(_author_id, _catalog_id, _page_no):
    _size_per_page = 5
    
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
        _a.reply_count = _reply_counts.get(_a.id, 0)
    
    return {
            'author_id': _author_id,
            'articles': _articles, 
            'catalogs':_catalogs, 
            'current_page_no':_page_no,
            'max_page_no': _max_page_no,
            'prefix_url': _remove_page_from_url(request.base_url),
            'editable': _author_id == _get_current_user_id(),
            }


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
            
        _articles = _query.order_by(desc(Article.published_datetime), desc(Article.id))[_offset:_offset+_size]
        return _articles
    
    
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
    
    
def _remove_page_from_url(_url):
    _p = re.compile(r'(.*)/p/\d*$')
    _m = re.match(_p, _url)
    
    if _m:
        return _m.group(1)
    else:
        return _url
    
    
@mod.route('/blog/<int:_author_id>/latest_articles/')
@template()
def list_latest_articles_by_author(_author_id):
    with get_scoped_db_session() as _dbss:
        _articles = _dbss.query(Article.id, Article.title)\
                                        .filter(Article.author_id==_author_id)\
                                        .order_by(desc(Article.published_datetime))[:10]
        
        return _articles
    
    
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
    

 

@mod.route('/article/<int:_article_id>')
@template(name='article.html')
def view_article(_article_id):
    with get_scoped_db_session(False) as _dbss:
        _article = _dbss.query(Article).options(joinedload(Article.content),
                                                joinedload(Article.author),
                                                joinedload(Article.keywords)).get(_article_id)
                                                
        _catalogs = _list_catalogs(_article.author_id)
                                                
    return {'author_id': _article.author_id,
            'article': _article, 
            'catalogs': _catalogs, 
            'editable': _article.author_id == _get_current_user_id()}


@mod.route('/article_reply/list/<int:_article_id>')
@template()
def list_replies_by_article(_article_id):
    _ref_datetime = request.args.get('_ref_datetime')
    _ref_id = request.args.get('_ref_id')
    
    with get_scoped_db_session(False) as _dbss:
        _query = _dbss.query(ArticleReply, 
                             User.id.label('author_id'), 
                             User.name.label('author_name'),
                             User.avatar.label('avatar'))\
                      .outerjoin(ArticleReply.author)\
                      .filter(ArticleReply.article_id==_article_id)
        
        if _ref_datetime and _ref_id:
            _query = _query.filter(ArticleReply.published_datetime<=_ref_datetime)\
                           .filter(ArticleReply.id<int(_ref_id))
        
        _replies = _query.order_by(desc(ArticleReply.published_datetime), \
                                   desc(ArticleReply.id))[0:2]
    
        return _replies
    
    
def _count_replies_by_articles(_article_ids):
    if _article_ids is None:
        _article_ids = []
    
    with get_scoped_db_session(False) as _dbss:
        _result_set = _dbss.query(ArticleReply.article_id, func.count(ArticleReply.id))\
                           .filter(ArticleReply.article_id.in_(_article_ids))\
                           .group_by(ArticleReply.article_id).all()
        
        return dict(_result_set)


@mod.route('/article_reply/new/', methods=['POST'])
@normal_user_permission.require()
@template()
def create_reply():
    _author_id = session['_user']['id']
    
    _article_id = request.form['_article_id']
    if _article_id: _article_id = int(_article_id)
       
    _reply = ArticleReply()
    _reply.article_id = _article_id
    _reply.content = request.form['_content']
    _reply.author_id = _author_id
    _reply.published_datetime = datetime.datetime.now()
       
    with get_scoped_db_session() as _dbss:
        _dbss.add(_reply)
        _dbss.flush()
           
        return {'_result': True,
                'reply_id': _reply.id, 
                'published_datetime': _reply.published_datetime}
        

@mod.route('/reply/delete/', methods=['POST'])
@template()
def delete_reply():
    _reply_id = request.form['reply_id']
    
    with get_scoped_db_session() as _dbss:
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
@normal_user_permission.require()
@template()
def create_catalog():
    _name = request.form['catalog_name']
    _owner_id = _get_current_user_id()
    
    with get_scoped_db_session() as _dbss:
        _count = _dbss.query(func.count(ArticleCatalog.id)).filter(ArticleCatalog.name==_name)\
                                                           .filter(ArticleCatalog.owner_id==_owner_id).scalar()
        
        if _count > 0:
            raise InvalidOperationException('已经存在同名的分类目录！')
        else:
            _new_catalog = ArticleCatalog(name=_name, owner_id=_owner_id)
            _dbss.add(_new_catalog)
            _dbss.flush()
    
            return {'_result': True, 'new_catalog_id': _new_catalog.id}


@mod.route('/catalog/edit/', methods=['POST'])
@normal_user_permission.require()
@template()
def edit_catalog():
    _id, _name = request.form['catalog_id'], request.form['catalog_name']
    _owner_id = _get_current_user_id()
        
    with get_scoped_db_session() as _dbss:
        _count = _dbss.query(func.count(ArticleCatalog.id)).filter(ArticleCatalog.name==_name)\
                                                           .filter(ArticleCatalog.owner_id==_owner_id).scalar()
        
        if _count > 0:
            raise InvalidOperationException('已经存在同名的分类目录！')
        else:
            _dbss.query(ArticleCatalog).filter_by(id=_id).update({'name':_name})
    
            return {'_result': True, }


@mod.route('/catalog/delete/', methods=['POST'])
@normal_user_permission.require()
@template()
def delete_catalog():
    _id = request.form['catalog_id']
    _owner_id = _get_current_user_id()
    
    with get_scoped_db_session() as _dbss:
        _catalog = _dbss.query(ArticleCatalog).get(_id)
        
        if _catalog.owner_id != _owner_id:
            raise InvalidOperationException('不能删除他人的分类目录！')
        
        _dbss.execute(association_table_catalog_article.delete()
                                                       .where(association_table_catalog_article.c.catalog_id==_id))  # @UndefinedVariable
        _dbss.delete(_catalog)
    
        return {'_result': True, }



    
    
