# coding: utf-8

from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.util import KeyedTuple
import datetime

def sa_obj_to_dict(obj, exclude_fields=[]):
    if isinstance(obj.__class__, DeclarativeMeta):
        _dict = {}
        for _k, _v in obj.__dict__.iteritems():
            if not _k.startswith('_') and _k not in exclude_fields:
                _v = sa_obj_to_dict(_v, exclude_fields)
                _dict[_k] = _v
            
        return _dict
    
    elif isinstance(obj, KeyedTuple):
        _dict = {}
        for _k, _v in obj._asdict().iteritems():
            _dict[_k] = sa_obj_to_dict(_v)
        
        return _dict
    
    elif isinstance(obj, list):
        _list = []
        for _item in obj:
            _list.append(sa_obj_to_dict(_item, exclude_fields))
        return _list
    
    elif isinstance(obj, datetime.datetime):
        return datetime.datetime.strftime(obj, '%Y-%m-%d %H:%M:%S')
    
    elif isinstance(obj, dict):
        _dict = {}
        for _k, _v in obj.iteritems():
            _v = sa_obj_to_dict(_v, exclude_fields)
            _dict[_k] = _v
            
        return _dict
           
    else:
        return obj