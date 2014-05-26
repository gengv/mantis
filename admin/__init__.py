#coding: utf-8

from contextlib import contextmanager
from database import db_session, get_scoped_db_session
from flask.blueprints import Blueprint
from flask.globals import request
from intercepter import template
from model import ArticleCatalog, Article, ArticleContent, \
    association_table_catalog_article, ArticleReply
from sqlalchemy.orm import joinedload, load_only
import datetime

mod = Blueprint('admin', __name__, static_folder='static', template_folder='templates')


@mod.route('/article_list/<int:_author_id>/', defaults={'_catalog_id': 0})
@mod.route('/article_list/<int:_author_id>/<int:_catalog_id>')
@template()
def list_articles(_author_id, _catalog_id):
    with get_scoped_db_session(False) as _dbss:
        if _catalog_id:
            _articles = _dbss.query(Article).join(Article.catalogs)\
                                            .filter(Article.author_id==_author_id)\
                                            .filter(ArticleCatalog.id==_catalog_id).all()  # @UndefinedVariable
        else:
            _articles = _dbss.query(Article).options(joinedload(Article.catalogs))\
                                            .filter_by(author_id=_author_id).all()
    
    return _articles


@mod.route('/article/new/', methods=['POST'])
def create_article():
    _title, _author_id, _digest, _content, _catalogs = \
        request.form['title'], \
        request.form['author_id'], \
        request.form['digest'], \
        request.form['content'], \
        request.form.getlist['catalog_id']
        
    _now = datetime.datetime.now()
    _new_article = Article(title=_title, 
                           author_id=_author_id,
                           digest=_digest,
                           content=ArticleContent(_content),
                           published_datetime=_now,
                           last_modified_datetime=_now)
    
    with get_scoped_db_session() as _dbss:
        _dbss.add(_new_article)
        _dbss.flush()
        
        for _cid in _catalogs:
            _dbss.execute(association_table_catalog_article.insert().values({
                                                                             'catalog_id': _cid,
                                                                             'article_id': _new_article.id,
                                                                             }))
        
    return 'Article created [%s][%s]' % (_new_article.id, _new_article.title)

@mod.route('/article/edit/', methods=['POST'])
def edit_article():
    _id, _title, _author_id, _digest, _content, _catalogs = \
        request.form['id'], \
        request.form['title'], \
        request.form['author_id'], \
        request.form['digest'], \
        request.form['content'], \
        request.form.getlist['catalog_id']
        
    with get_scoped_db_session() as _dbss:
        _article = _dbss.query(Article).options(load_only(Article.id)).filter_by(id=_id).one()
        _article.title = _title
        _article.digest = _digest,
        _article.content.content = _content,
        _article.last_modified_datetime = datetime.datetime.now()
        
        _dbss.flush()
        
        _dbss.execute(association_table_catalog_article.delete()\
                                                       .where(association_table_catalog_article.c.article_id==_id))  # @UndefinedVariable
        for _cid in _catalogs:
            _dbss.execute(association_table_catalog_article.insert().values({
                                                                             'catalog_id': _cid,
                                                                             'article_id': _id,
                                                                             }))
            
            
    
    return 'Article updated [%s][%s]' % (_article.id, _article.title)


@mod.route('/article/remove/', methods=['POST'])
def remove_article():
    _id = request.form['id']
    
    with get_scoped_db_session() as _dbss:
        _dbss.query(Article).filter_by(id=_id).update({'state': Article.HIDDEN})
        
    return 'Article removed [%s]' % _id


@mod.route('/article/remove_batch/', methods=['POST'])
def remove_article_batch():
    _ids = request.form.getlist('id')
    
    with get_scoped_db_session() as _dbss:
        for _id in _ids:
            _dbss.query(Article).filter_by(id=_id).update({'state': Article.HIDDEN})
        
    return 'Article batch removed [%s]' % (','.join([str(_id) for _id in _ids]))


@mod.route('/article/delete/', methods=['POST'])
def delete_article():
    _id = request.form['id']

    with get_scoped_db_session() as _dbss:
        _dbss.execute(association_table_catalog_article.delete()
                                                       .where(association_table_catalog_article.c.article_id==_id))  # @UndefinedVariable
        _dbss.query(Article).filter_by(id=_id).delete()
    
    return 'Article deleted [%s]' % _id


@mod.route('/reply/delete/', methods=['POST'])
def delete_reply():
    _reply_id = request.form['id']
    
    with get_scoped_db_session() as _dbss:
        _dbss.query(ArticleReply).filter_by(id=_reply_id).delete()
        
    return 'Reply deleted [%s]' % _reply_id


@mod.route('/catalog/new/', methods=['POST', 'GET'])
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
def edit_catalog():
    if request.method == 'POST':
        _id, _name = request.form['id'], request.form['name']
    else:
        _id, _name = request.args.get('id'), request.args.get('name')
        
    with get_scoped_db_session() as _dbss:
        _dbss.query(ArticleCatalog).filter_by(id=_id).update({'name':_name})
    
    return 'ArticleCatalog renamed [%s][%s]' % (_id, _name)


@mod.route('/catalog/delete/', methods=['POST', 'GET'])
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


