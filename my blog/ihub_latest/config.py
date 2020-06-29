# divide config
# use  and test
import redis


class Config:
    DEBUG = True

    ''' 配置信息'''
    SECRET_KEY = 'gnoianegpangpaehreahbsdhrst'

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/thub"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask-session配置 baidu.com docs
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie 中session_id 进行隐藏处理

    PERMANENT_SESSION_LIFTIME = 86400  # 24小时


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
