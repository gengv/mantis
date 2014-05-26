# coding: utf-8
from database.utils import sa_obj_to_dict
from flask.globals import request
from flask.templating import render_template
import functools
import json



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
        