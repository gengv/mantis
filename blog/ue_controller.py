# coding: utf-8
from flask.blueprints import Blueprint
from flask.globals import request
from intercepter import template
import json
import random
import re

mod = Blueprint('blog_ue_ctrlr', __name__)

@mod.route('/controller/', methods=['GET', 'POST'])
@template()
def ue_control():
    _action = request.args['action']
    
    if _action == 'config':
        return _parse_ue_config_json()
    
    elif _action == 'uploadimage':
        _file = request.files.get('upfile')
        _file.save(r'D:/test/%s' % random.randint(1000, 9999))
         
        return {
                'state': 'SUCCESS',
                'url': 'test-url',
                'title': 'test-title',
                'original': 'test-original',
                }
    

def _parse_ue_config_json():
    with open('public/static/ue/config/config.json', 'r') as _config_file:
        _json_content = ''.join(_config_file.readlines())
        _json_content = re.sub("\/\*[\s\S]+?\*\/", "", _json_content)
        
        return json.loads(_json_content)  
