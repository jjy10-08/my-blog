from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy

from flask_session import Session
from flask_wtf import CSRFProtect

import redis

from ihub.utils.commons import ReConverter

# database
db = SQLAlchemy()

# 创建redis链接对象
redis_store = None


# Production modle
def create_app(config_name):
    '''
    create flask's app object
    :param config_name: str  can be choose modle('develop','product')
    :return: app
    '''
    app = Flask(__name__)
    # According to config's name to acquire the class of config param.
    config_cls = config_map.get(config_name)
    app.config.from_object(config_cls)

    # use app to init db
    global redis_store
    db.init_app(app)
    
    # init tool of redis
    redis_store = redis.StrictRedis(host=config_cls.REDIS_HOST, port=config_cls.REDIS_PORT)

    # 利用flask-session,将session 数据保存到redis中去
    Session(app)  # Session

    # csrf protect
    CSRFProtect(app)
    # 为flask 添加自定义的转换器
    app.url_map.converters["re"] = ReConverter
    # register blueprint
    from ihub import api_1_0  # solve loop import
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    # 注册提供静态文件的蓝图
    from ihub.web_html import html
    app.register_blueprint(html)

    return app
