from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihub.utils.response_code import RET
import functools


# 定义正则转换器
class ReConverter(BaseConverter):

    # def __init__(self, url_map, regex):
    #     # 调用父类初始化方法
    #     super(ReConverter).__init__(url_map)
    #     # 保存正则表达式
    #     self.regex = regex
    def __init__(self, url, *args):
        super(ReConverter, self).__init__(url)
        self.regex = args[0]

# 定义的验证登录的装饰器
def login_required(vie_func):
    @functools.wraps(vie_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session("user_id")
        # 如果用户是登录的,执行view_func
        if user_id is not None:
            # 将user_id 保存到g对象，在试图函数中通过g 获取保存的数据
            g.user_id = user_id
            return vie_func(*args, **kwargs)
        else:
            # 如果未登录,返回未登录的信息
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    return wrapper


