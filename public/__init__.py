# coding: utf-8
from flask.blueprints import Blueprint

mod = Blueprint('public', __name__, static_folder='static', template_folder='templates')