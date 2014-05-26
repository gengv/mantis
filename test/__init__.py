from database import get_scoped_db_session
from model import Article, ArticleCatalog, ArticleReply, User
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import desc, distinct
from sqlalchemy.sql.functions import func
import datetime

with get_scoped_db_session(False) as _dbss:
#         print _dbss.query(func.count(Article.id)).join(Article.catalogs)\
#                                      .filter(Article.author_id==5)\
#                                      .filter(ArticleCatalog.id==10).scalar()
                                     
#     _articles = _dbss.query(Article).join(Article.catalogs)\
#                                             .filter(Article.author_id==5)\
#                                             .filter(ArticleCatalog.id==1)\
#                                             .order_by(Article.published_datetime)[1:3]
                                            
#     _articles = _dbss.query(Article).options(joinedload(Article.catalogs))\
#                                             .filter_by(author_id=5)\
#                                             .order_by(Article.published_datetime)[1:3]
                                            
#     print _dbss.query(func.count(Article.id))\
#                       .join(Article.catalogs)\
#                       .filter(Article.author_id==5).scalar()

#     _articles = _dbss.query(Article).options(joinedload(Article.catalogs))\
#                                             .filter_by(author_id=5)[0:5]
                                            
#     _articles = _dbss.query(Article).filter_by(Article.catalogs.any(ArticleCatalog.id=))[0:5]
#                                             
#     print len(_articles)

#     import re
#     
# #     _p = re.compile('(.*)/p/\d*$')
#     _p = re.compile(r'(.*)/p/\d*$')
#     _m = re.match(_p, "http://127.0.0.1:5000/blog/b/5/p/36")
#     
#     print _m.group(1)

#         _replies = _dbss.query(ArticleReply, User.id, User.name)\
#                         .outerjoin(ArticleReply.author)\
#                         .filter(ArticleReply.article_id==196)\
#                         .order_by(ArticleReply.published_datetime).all()
#                         
#         print _replies

#     _dbss.query(Article, func.count(ArticleReply.id)).join(Article.catalogs)\
#                                          .filter(Article.author_id==5)\
#                                          .filter(ArticleCatalog.id==2).join(Article.replies).group_by(Article).all()

    _stmt = _dbss.query(Article.id.label('article_id'), func.count(ArticleReply.id).label('reply_count')).filter(Article.id==ArticleReply.article_id).group_by(Article.id).subquery()
    _r = _dbss.query(Article, _stmt.c.reply_count).distinct(Article.id).join(Article.catalogs)\
                                         .filter(Article.author_id==5)\
                                         .filter(ArticleCatalog.id==2).filter(Article.id==_stmt.c.article_id).order_by(desc(Article.published_datetime))[0:3]                                 
     
    print len(_r) 
    for _i in _r:
        print _i, _i [0].id 
        
    print "------------------"            
                        
    _stmt = _dbss.query(Article).join(Article.catalogs)\
                                         .filter(Article.author_id==5)\
                                         .filter(ArticleCatalog.id==2).subquery()
                                         
    _r = _dbss.query(_stmt, func.count(ArticleReply.id).label('reply_count')).filter(_stmt.c.id==ArticleReply.article_id).group_by(_stmt)[0:3]
    print len(_r) 
    for _i in _r:
        print _i, _i[0]
                                         
                                         
#     _dbss.query(Article, func.count(ArticleReply.id)).filter(Article.author_id==5)\
#                                          .join(Article.replies).group_by(Article).all()