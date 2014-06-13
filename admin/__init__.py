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









def _list_catalogs(_owner_id):
    with get_scoped_db_session(False) as _dbss:
        _catalogs = _dbss.query(ArticleCatalog).filter_by(owner_id=_owner_id).all()
        return _catalogs
    




