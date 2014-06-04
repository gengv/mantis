# coding: utf-8
from database import Base
from enum import ArticleEnum
from sqlalchemy.orm import deferred, relationship, backref
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.schema import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Text, DateTime

class TableNameConst(object):
    USER = 'user'
    ROLE = 'role'
    ARTICLE = 'article'
    ARTICLE_CONTENT = 'article_content'
    ARTICLE_CATALOG = 'article_catalog'
    ARTICLE_REPLY = 'article_reply'
    KEYWORD = 'keyword'
    
    ASSOCIATION_CATALOG_ARTICLE = 'asso_catalog_article'
    ASSOCIATION_ARTICLE_KEYWORD = 'asso_article_keyword'
    ASSOCIATION_USER_ROLE = 'asso_user_role'
    

class Role(Base):
    __tablename__ = TableNameConst.ROLE
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    

class User(Base):
    __tablename__ = TableNameConst.USER
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    passcode = deferred(Column(String(32), nullable=False))
    email = deferred(Column(String(300), nullable=False))
    avatar = Column(String(300))
    
    roles = relationship(Role, secondary=TableNameConst.ASSOCIATION_USER_ROLE, backref='users')
    
    
association_table_user_role = \
    Table(TableNameConst.ASSOCIATION_USER_ROLE, Base.metadata,
          Column('user_id', Integer, ForeignKey('%s.id' % TableNameConst.USER)),
          Column('role_id', Integer, ForeignKey('%s.id' % TableNameConst.ROLE)),
          mysql_engine='InnoDB')
    
    
class ArticleCatalog(Base):
    __tablename__ = TableNameConst.ARTICLE_CATALOG
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    
    owner_id = Column(Integer, ForeignKey(User.id))
    owner = relationship(User, backref=backref('article_catalogs'))
    
    
class Keyword(Base):
    __tablename__ = TableNameConst.KEYWORD
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    

class ArticleContent(Base):
    __tablename__ = TableNameConst.ARTICLE_CONTENT
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    
    article_id = Column(Integer, ForeignKey('%s.id' % TableNameConst.ARTICLE, ondelete='CASCADE'))
    
    
class ArticleReply(Base):
    __tablename__ = TableNameConst.ARTICLE_REPLY
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    published_datetime = Column(DateTime)
    
    author_id = Column(Integer, ForeignKey(User.id))
    author = relationship(User, backref=backref('replies', order_by=id))
    
    article_id = Column(Integer, ForeignKey('%s.id' % TableNameConst.ARTICLE, ondelete='CASCADE'))
    
    
association_table_catalog_article = \
    Table(TableNameConst.ASSOCIATION_CATALOG_ARTICLE, Base.metadata,
          Column('catalog_id', Integer, ForeignKey('%s.id' % TableNameConst.ARTICLE_CATALOG)),
          Column('article_id', Integer, ForeignKey('%s.id' % TableNameConst.ARTICLE)),
          mysql_engine='InnoDB')
    
association_table_article_keyword = \
    Table(TableNameConst.ASSOCIATION_ARTICLE_KEYWORD, Base.metadata,
          Column('article_id', Integer, ForeignKey('%s.id' % TableNameConst.ARTICLE)),
          Column('keyword_id', Integer, ForeignKey('%s.id' % TableNameConst.KEYWORD)),
          mysql_engine='InnoDB')
    

class Article(Base, ArticleEnum):
    __tablename__ = TableNameConst.ARTICLE
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    digest = Column(String(400))
    state = Column(Integer)
    published_datetime = Column(DateTime)
    last_modified_datetime = Column(DateTime)
    
    author_id = Column(Integer, ForeignKey(User.id))
    author = relationship(User, backref=backref('articles', order_by=id))
    
    content = relationship(ArticleContent, uselist=False, cascade='all, delete, delete-orphan')
    
    replies = relationship(ArticleReply, order_by=ArticleReply.published_datetime, cascade_backrefs='all, delete-orphan', backref='article')
    
    catalogs = relationship(ArticleCatalog, secondary=association_table_catalog_article,
                            backref='articles')
    keywords = relationship(Keyword, secondary=association_table_article_keyword,
                            backref='articles')
    

if __name__ == '__main__':
    from database import engine    
    Base.metadata.create_all(engine)