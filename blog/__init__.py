# coding: utf-8
from database import get_scoped_db_session
from flask.blueprints import Blueprint
from flask.globals import request
from intercepter import template
from model import Article, ArticleCatalog, ArticleReply, User
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.functions import func
import datetime
import math
import re

mod = Blueprint('blog', __name__, static_folder='static', template_folder='templates')

# @mod.route('/', methods=['POST', 'GET'])
@template(name='index.html')
def index():
    return {}

@mod.route('/b/<int:_author_id>', defaults={'_page_no': 1})
@mod.route('/b/<int:_author_id>/p/<int:_page_no>')
def list_articles_by_author(_author_id, _page_no):
    return _list_articles(_author_id=_author_id, _page_no=_page_no)

@mod.route('/b/<int:_author_id>/c/<int:_catalog_id>', defaults={'_page_no': 1})
@mod.route('/b/<int:_author_id>/c/<int:_catalog_id>/p/<int:_page_no>')
def list_articles_by_author_and_category(_author_id, _catalog_id, _page_no):
    return _list_articles(_author_id=_author_id, _catalog_id=_catalog_id, _page_no=_page_no)

@template(name='index.html')
def _list_articles(_author_id, _catalog_id=None, _page_no=1):
    _count_of_articles = count_articles(_author_id, _catalog_id)
    _size_per_page = 5
    _max_page_no = int(math.ceil((1.0*_count_of_articles/_size_per_page)))
    
    if _page_no > _max_page_no: _page_no = _max_page_no
    
    _offset = (_page_no-1) * _size_per_page
    
    
    with get_scoped_db_session(False) as _dbss:
        _query = _dbss.query(Article).join(Article.catalogs)\
                                     .filter(Article.author_id==_author_id)
        if _catalog_id:
            _query = _dbss.query(Article).join(Article.catalogs)\
                                         .filter(Article.author_id==_author_id)\
                                         .filter(ArticleCatalog.id==_catalog_id)
                                         
        else:
            _query = _dbss.query(Article).filter_by(author_id=_author_id)
        
        _articles = _query.order_by(Article.published_datetime)[_offset:_offset+_size_per_page]
    
    _catalogs = list_catalogs(_author_id)
    
    
    print 'script_root:', request.base_url
    
    
    return {
            'articles': _articles, 
            'catalogs':_catalogs, 
            'current_page_no':_page_no,
            'max_page_no': _max_page_no,
            'prefix_url': remove_page_from_url(request.base_url)
            }
    
def remove_page_from_url(_url):
    _p = re.compile(r'(.*)/p/\d*$')
    _m = re.match(_p, _url)
    
    if _m:
        return _m.group(1)
    else:
        return _url
 

@mod.route('/article/<int:_article_id>')
@template(name='article.html')
def view_article(_article_id):
    with get_scoped_db_session(False) as _dbss:
        _article = _dbss.query(Article).options(joinedload(Article.content),
                                                joinedload(Article.author),
                                                joinedload(Article.keywords)).get(_article_id)
                                                
        _catalogs = list_catalogs(_article.author_id)
                                                
    return {'article': _article, 'catalogs': _catalogs}


@mod.route('/article_reply/<int:_article_id>')
@template()
def list_replies_by_article(_article_id):
    _ref_datetime = request.args.get('_ref_datetime')
    _ref_id = request.args.get('_ref_id')
    
    with get_scoped_db_session(False) as _dbss:
        _query = _dbss.query(ArticleReply, User.id.label('author_id'), User.name.label('author_name'))\
                      .outerjoin(ArticleReply.author)\
                      .filter(ArticleReply.article_id==_article_id)
        
        if _ref_datetime and _ref_id:
            _query = _query.filter(ArticleReply.published_datetime<=_ref_datetime)\
                           .filter(ArticleReply.id<int(_ref_id))
        
        _replies = _query.order_by(desc(ArticleReply.published_datetime), \
                                   desc(ArticleReply.id))[0:2]
    
    return _replies


@mod.route('/add_article_reply/', methods=['POST'])
@template()
def create_reply():
    _author_id = 1
    _article_id = request.form['_article_id']
    if _article_id: _article_id = int(_article_id)
       
    _reply = ArticleReply()
    _reply.article_id = _article_id
    _reply.content = request.form['_content']
    _reply.author_id = _author_id
    _reply.published_datetime = datetime.datetime.now()
       
    print _article_id, _reply.content, _reply.published_datetime
       
    with get_scoped_db_session() as _dbss:
        _dbss.add(_reply)
        _dbss.flush()
           
        return {'reply_id': _reply.id, 
                "published_datetime": _reply.published_datetime}
    

def list_catalogs(_owner_id):
    with get_scoped_db_session(False) as _dbss:
        _catalogs = _dbss.query(ArticleCatalog).filter_by(owner_id=_owner_id).all()
        
    return _catalogs


def count_articles(_author_id, _catalog_id):
    with get_scoped_db_session(False) as _dbss:
        _query = _dbss.query(func.count(Article.id))\
                                     
        if _catalog_id:
            _query = _query.join(Article.catalogs).filter(Article.author_id==_author_id)\
                                                  .filter(ArticleCatalog.id==_catalog_id)
        else:
            _query = _query.filter(Article.author_id==_author_id)
            
        _count = _query.scalar()
            
        return _count
