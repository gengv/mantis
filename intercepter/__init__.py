# coding: utf-8
from database.utils import sa_obj_to_dict
from flask.globals import request
from flask.templating import render_template
from werkzeug.contrib.cache import SimpleCache
import functools
import json
import logging


def template(name=None, path=None):
    def _template(func):
        
        @functools.wraps(func)
        def _decorated(*args, **kwargs):
            _result = func(*args, **kwargs)
            
            if request.is_xhr or name is None:
                return json.dumps(sa_obj_to_dict(_result))
            
            else:
                if type(_result)==dict:
                    return render_template(name, **_result)
                else:
                    return _result
                
        return _decorated
    return _template


cache_repo = SimpleCache()
default_timeout = 300

def cached(name=None, timeout = default_timeout):
    def _cached(func):
        @functools.wrap(func)
        def _decorated(*args, **kwargs):
            args_list = list(args)
            args_str = ','.join([str(a) for a in args_list]) if args_list else ''
            
            kwargs_dict = dict(kwargs)
            kwargs_str = ','.join(['%s=%s' % (k, kwargs_dict[k]) for k in sorted(kwargs_dict.keys())])
                
            cache_key = 'method/%s?%s,%s' % (func.__name__, args_str, kwargs_str)
            
            result = cache_repo.get(cache_key)
            if result:
                logging.debug('Read Cache [%s].' %cache_key)
                return result
            else:
                result = func(*args, **kwargs)
                cache_repo.set(cache_key, result, timeout=timeout)
                logging.debug('Save Cache [%s].' %cache_key)
                return result
            
        return _decorated
    return _cached
        