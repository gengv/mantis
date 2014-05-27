# coding: utf-8

from contextlib import contextmanager
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker

engine = create_engine("mysql://gengv:nkc0ma@localhost/mantis", echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

Base.__table_args__ = {'mysql_engine':'InnoDB'}

@contextmanager
def get_scoped_db_session(auto_commit=True):
    _dbss = db_session()
    try:
        yield _dbss
        if auto_commit:
            _dbss.commit()
        
    except Exception, e:
#         import sys
#         print sys.exc_info()[1]
        _dbss.rollback()
        raise e
    
    finally:
        _dbss.close()