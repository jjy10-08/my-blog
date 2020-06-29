'''
    注册登录认证
'''
import re

from ihub.models import User
from . import api
from flask import request, jsonify, session
from ihub.utils.response_code import RET
from ihub import constants, redis_store, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


#  POST 127.0.0.1:5000/api/v1.0/register
@api.route("/register", methods=['POST'])
def register():
    '''
    注册视图!
    请求的参数:密码, 账号
    参数格式:json
    '''
    # 获取请求的json数据,返回字典
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 校验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码格式错误")
    # 从redis 中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='读取短信验证码异常')
    # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码失效')
    # 删除redis 中的记录防止重复校验
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        pass
    # 判断用户填写短信验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    # 判断用户的手机号是否注册过
    # try:
    #     user =User.querry.filter_by(mobile).first()
    # except Exception as e:
    #     return jsonify(errno=RET.DBERR,errmsg='数据库异常')
    # else :
    #     if user is not None:
    #         # 手机号已经存在
    #         return jsonify(errno=RET.DATAEXIST,errmsg='手机号已经存在')
    # 保存用户的注册数据到数据库中

    user = User(name=mobile, mobile=mobile)
    # user.generate_password_hash(password)
    user.password = password  # 设置属性

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollbacak()
        # 手机号出现了重复值
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


# 127.0.0.1:5000/api/v1.0/sessions
@api.route("/sessions", methods=["POST"])
def login():
    '''
    用户登录
    :param: mobile , pswd
    '''
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")
    # 校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 手机号的格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    # 判断错误次数是否超过限制，如果超过限制返回
    # redis 记录: access_nums_请求的Ip地址 ：次数
    user_ip = request.remote_addr  # 用户的ip地址
    try:
        access_nums = redis_store.get("access_nums_%s" % user_ip)
    except Exception as e:
        pass
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多,稍后再试")
    # 从数据库中根据手机号查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 用数据库的密码与用户填写的密码进行对比验证
    if user is None or not user.check_password(password):
        # 验证失败记录错误次数 返回信息
        try:
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            pass
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")
    # 如果验证相同成功，保存登录状态，在session中
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.user_id

    return jsonify(errno=RET.OK, errmsg="登录成功")


# 127.0.0.1:5000/api/v1.0/session
@api.route("/session", methods=["GET"])
def check_login():
    '''
    检查登录状态
    :return:
    '''
    # 从session中获取用户的名字
    name = session.get["name"]
    # 如果session 中 name 存在,表示用户已登录,否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


# 127.0.0.1:5000/api/v1.0/session
@api.route("/session", methods=["DELETE"])
def logout():
    '''
    登出
    :return:
    '''
    # 清除session数据
    session.clear()
    return jsonify(errno=RET.OK, errmsg="OK")
