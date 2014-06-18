# coding: utf-8
from flask.blueprints import Blueprint

mod = Blueprint('file_storage', __name__, static_folder='static')

