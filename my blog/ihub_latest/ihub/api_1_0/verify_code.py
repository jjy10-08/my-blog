import random

from . import api
from ihub.utils.captcha.captcha import captcha
from ihub import redis_store, constants, db
from flask import jsonify, make_response, request
from ihub.utils.response_code import RET
from ihub.models import User
from ihub.libs.yuntongxun.SendTemplateSMS import CCP


# 后端接口定义的规范
# Restful 规范风格并不强制表现层状态转化
# 数据的操作 增删改查
# goods 的url 不规范的使用 --- 麻烦
# /add_goods
# /update_goods
# /delete_goods
# /get_goods

#  不要定义四个路径 定义一个路径
#  /goods
# http 请求方式  GET POST PUT DELETE 对应增删改查
# #GET 查询
# POST 保存
# PUT 修改
# DELETE　删除
# 资源的表现形式 txt格式  html 格式 json 格式 jpg格式 。。等 浏览器通过URL 确定资源的位置但需要在HTTP 请求头中,用Accept和Content-Type字段指定,这两个字段是对资源表现的描述
# 状态转换. 其中,GET 表示获取资源 POST 新建, PUT表示更新,DELETE 表示删除
# 在看蓝图中确定版本
# eg : GET http:www.example.com/goods/id  获取指定商品的信息
# : POST http:www.example.com/goods 新建商品信息
# PUT http: www.example.com/goods/id 更改指定商品信息
# DELETE　http:www.example.com/goods/id 删除指定商品信息

# 如果资源信息过多服务器不能一次返回则 一次全部返回 API 提供参数
# eg:? 方式一
# http://www.example.com/goods?limit =10 指定返回数据的数量
# http://www.example.com/goods?offest=10 指定返回数据的开始位置
# http://www.example.com/goods?page=2&per_page =20 # 指定第几页,以及每页数据的数量

# http的状态码 服务器向用户返回的状态码和提示信息
# 200 OK ： 服务器成功返回用户请求的数据  --GET
# 201 CREATED: 用户新建或修改数据成功  --- POST PUT
# 202 Accept: 表示请求已经进入后台排队
# 400 INVALID REQUEST  : 用户发送的请求有错误
# 401 Unauthorized : 用户没有权限
# 403 Forbidden :访问被禁止
# 404 NOT FOUND： 请求针对的是不存在的记录
# 406 Not Acceptable ：用户请求的格式不正确
# 500 INTERNAL SERVER ERROR  :服务器发生错误
# # 方式二 json 数据包:  { 'errcode':40029 ,'errmsg':invalid code}

# 一般来说服务器返回的信息以键值对的方式来返回
# {error：'Invalid API KEY'}
# ---------------------------------------------
# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
### GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@api.route('/image_codes/<image_code_id>')  # 路由的选定 根据规范
def get_image_code(image_code_id):
    '''
     get
    :params image_code_id:图片验证码编号
    :return:正常情况 返回 验证码图片 异常:返回json
    '''
    # 获取参数 该状态下前端会给
    # 检验参数

    # 业务逻辑处理:
    # 生成验证码图片 captcha 包
    # 名字 真真实文本 图片数据
    name, text, image_data = captcha.generate_captcha()
    # 将验证码真实值与编号保存到redis 中,设置有效期
    # redis: 字符串 列表 哈希 set
    # 'key':xxx
    # 'image_codes':{"id1":"abc","":"","":""} 哈希 hset("image_codes","id1","abc")
    # hget("image_codes","id1")
    # 使用哈希维护有效期的时候只能整体设置

    # 单条维护记录,选用字符串
    # "image_code_编号1":"真实值"
    # redis_store.set('image_code_%s' % image_code_id, text)
    # redis_store.expire('image_code_%s'% image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES)
    # 记录名字 有效期 记录值
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 记录日志--- current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='保存图片验证码失败')

    # 返回图片
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/ipg"
    return resp


# GET 127.0.0.1:5000/api/v1.0/sms_codes/<mobile>
@api.route("/sms_code/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    '''
    获取短信验证码 get
    '''
    # 获取参数
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')
    # 校验参数
    if not all([image_code_id, image_code]):
        # 参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 业务逻辑处理
    # 从redis 中取出真实的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='redis数据库异常')
    # 判断图片验证码是否过期
    if real_image_code is None:
        # 表示图片验证码没有或者过期
        return jsonify(errno=RET.NODATA, errmsg='图片验证失效')
    # 删除redis中图片验证码 防止一张图重复多次验证
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        pass

        # 进行用户填写的值的对比
    if real_image_code.lower() != image_code.lower():
        # 表示用户填写错误
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码失败')

    # 判断对于这个手机号的操作,在60秒内有没有之前的记录，如果有,认为操作频繁，不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        pass
    else:
        if send_flag is not None:
            # 表示60s 内重复发送
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁")

    # 判断手机号是否存在(数据库的查询)
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        pass  #
    else:
        if user is not None:
            # 表示手机号存在
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经存在')
    # 如果手机号不存在,则生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)
    # 保存真实的短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户60s内再次发出发送短信的操作
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码异常')
    # 发送短信
    try:
        ccp = CCP()
        res = ccp.sendTemplateSMS(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    except Exception as e:
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
        # 返回值
    if res == 0:
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")
