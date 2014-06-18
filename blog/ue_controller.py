# coding: utf-8
from flask.blueprints import Blueprint
from flask.globals import request
from intercepter import template
import base64
import datetime
import json
import os.path
import random
import re

mod = Blueprint('blog_ue_ctrlr', __name__)

UPLOAD_DIR = 'file_storage/static'

@mod.route('/controller/', methods=['GET', 'POST'])
@template()
def ue_control():
    _action = request.args['action']
    
    if _action == 'config':
        return _parse_ue_config_json()
    
    elif _action in ['uploadimage', 'uploadfile', 'uploadvideo']:
        _file = request.files.get('upfile')
        _file_path = _save_uploaded_file(_file)
         
        return {
                'state': 'SUCCESS',
                'url': _file_path,
                'title': _file.filename,
                'original': _file.filename,
                }
        
    elif _action == 'uploadscrawl':
        _b64string = request.form['upfile']
        
        _file_path = _save_uploaded_base64(_b64string, _ext='.png')
        
        return {
                'state': 'SUCCESS',
                'url': _file_path,
                'title': _file_path,
                'original': _file_path,
                }
        
    elif _action in ['listimage', 'catchimage']:
        return {
                'state': u'功能尚待开发！'
                }
    

def _parse_ue_config_json():
    with open('public/static/ue/config/config.json', 'r') as _config_file:
        _json_content = ''.join(_config_file.readlines())
        _json_content = re.sub("\/\*[\s\S]+?\*\/", "", _json_content)
        
        return json.loads(_json_content)
    

def _save_uploaded_file(_file):
    _now = datetime.datetime.now()
    _new_file_name = '%s_%s%s' % (_now.strftime('%Y-%m-%d_%H%M%S'), 
                                  random.randint(100000, 999999), os.path.splitext(_file.filename)[1])
    
    _dir_name = _now.strftime('%Y%m%d')
    
    _real_dir_path = os.path.join(os.getcwdu(), UPLOAD_DIR, _dir_name)
    
    if not os.path.isdir(_real_dir_path):
        os.makedirs(_real_dir_path)
    
    _file.save(os.path.join(_real_dir_path, _new_file_name))
    
    return '/'.join(['', UPLOAD_DIR, _dir_name, _new_file_name])


def _save_uploaded_base64(_b64string, _ext=''):
    _now = datetime.datetime.now()
    _new_file_name = '%s_%s%s' % (_now.strftime('%Y-%m-%d_%H%M%S'), 
                                  random.randint(100000, 999999), _ext)
    
    _dir_name = _now.strftime('%Y%m%d')
    
    _real_dir_path = os.path.join(os.getcwdu(), UPLOAD_DIR, _dir_name)
    
    if not os.path.isdir(_real_dir_path):
        os.makedirs(_real_dir_path)
        
    _decoded_string = base64.b64decode(_b64string)
    with open(os.path.join(_real_dir_path, _new_file_name), 'wb') as _f:
        _f.write(_decoded_string)
    
    return '/'.join(['', UPLOAD_DIR, _dir_name, _new_file_name])