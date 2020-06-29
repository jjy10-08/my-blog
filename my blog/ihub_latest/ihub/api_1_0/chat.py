'''
    用户聊天模块
'''
from . import api
from ihub.utils.commons import login_required
from flask import g,jsonify, request
from ihub.utils.response_code import RET
from ihub.utils.image_storage import storage
from ihub.models import User,Chatting,Query
from ihub import db
from ihub import constants