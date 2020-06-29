from . import api
from ihub.utils.commons import login_required
from flask import g, jsonify, request, session
from ihub.utils.response_code import RET
from ihub.utils.image_storage import storage
from ihub.models import User
from ihub import db
from ihub import constants


# /api/v1.0/users/profile
@api.route("/users/profile", methods=["POST"])
@login_required
def set_profile():
    user_id = g.user_id
    # 获取参数
    req_dict = request.get_json()
    class_num = req_dict("class_num")
    # name = req_dict("name")
    introduce = req_dict("introduce")
    # 保存用户信息到数据库中(未填写即"")
    try:
        User.query.filter_by(id=user_id).update({"class_num": class_num, "introduce": introduce})
        db.session.commit()
    # 不正确返回
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")
    # 正确返回
    return jsonify(errno=RET.OK, errmsg="修改成功")


# /api/v1.0/users/avatar
@api.route("/users/avatar", methods=["POST"])
@login_required
def set_avatar():
    user_id = g.user_id
    # 获取图片(参数)
    image_file = request.files.get("avatar")
    if image_file is None:
        return jsonify(errno=RET.DBERR, errmsg="未上传图片")
    image_data = image_file.read()

    # 调用七牛上传图片 返回文件名
    try:
        file_name = storage(image_data)
    except Exception as e:
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")
    # 保存文件名到数据库
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": constants.QINIU_URL_PREFIX + file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片信息失败")
    return jsonify(errno=RET.OK, errmsg="保存成功")


# 昵称修改
@api.route("/user/name", methods=["PUT"])
@login_required
def change_user_name():
    # 获取想要设置的id
    user_id = g.user_id
    name = request.get_json().get("name")
    if name is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")
    # 保存昵称
    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

        # 修改session中的name 字段
    session["name"] = name
    # 返回
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 加载信息接口
@api.route("/user", methods=["GET"])
@login_required
def show_profile():
    '''获取个人信息
    :return:
    '''
    # g.user_id
    user_id = g.user_id

    # 查询数据库获取个人信息
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="加载信息失败")

    # 向前端返回信息
    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())
