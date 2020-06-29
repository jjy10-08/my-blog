# 保存图片验证码的 redis有效期 单位秒
IMAGE_CODE_REDIS_EXPIRES = 180

# 再redis 中的有效期
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的时间间隔
SEND_SMS_CODE_INTERVAL = 60
# session数据有效期， 单位秒
SESSION_EXPIRES_SECONDS = 86400
# 登录错误尝试次数
LOGIN_ERROR_MAX_TIMES = 5

# 登录错误限制的时间 秒
LOGIN_ERROR_FORBID_TIME = 600

# 七牛存储空间的域名
QINIU_URL_PREFIX = "http://别忘记改!/"  
