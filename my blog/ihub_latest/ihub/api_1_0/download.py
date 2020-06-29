
from . import api
from ihub.utils.commons import login_required
from flask import g,jsonify, request
from ihub.utils.response_code import RET
from ihub.utils.image_storage import storage
from ihub.models import Download
from ihub import db
from ihub import constants

#api/v1.0/download/filename
@api.route("/download/<file_name>", methods=["GET"])
@login_required
def download(file_name):
    '''
         下载功能的实现
    :param :file_name
    :return: '连接失败'  / '连接成功正在下载'
    '''
    # try:
    #     Download.query(Download.file_name=file_name)
    # except StatementError:
    #      return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')
    try:
        download_info=Download.query.filter_by(file_name=file_name).first()
        url_path=download_info.url_path
    except Exception as e :
        return jsonify(errno=RET.DBERR,errmsg="数据异常")
    urls="/tarena/ediliwc/ftp"+url_path

    try:
        file = open(urls,"rb")
    except Exception as e :
        return  jsonify(errno=RET.IOERR,errmsg="获取下载资源失败")

    data=file.read()

    return jsonify(errno=RET.OK,errmsg="ok",data=data)


# api/v1.0/download/search/
# 示例:<re(r'1[34578]\d{9})':mobile>"
@api.route("/download/search", methods=["GET"])
@login_required
def search_file():
    key_words = request.args.get("keywords")
    # 字段的处理:
    key_words = key_words.lower().replace(" ", "")
    if "python" in key_words:
        key_words = key_words.replace("python", "")
        tag = "python,%s" % key_words
        try:
            d_list = Download.query.filter_by(describe=tag).all()  # 列表
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg="查询异常")
        res = []
        if not d_list:
            for elem in d_list:
                res.append(elem.file_name)
            return jsonify(errno=RET.OK, errmsg="OK", data=res)
        else:
            # 给10条python 相关信息?
            return jsonify(errno=RET.OK, errmsg="无此信息")

    else:
        return jsonify(errno=RET.OK, errmsg="搜索功能完善中")

    # result = []
    # for item in os.listdir(path):
    #     item_path = os.path.join(path, item)
    #     if os.path.isdir(item_path):
    #         search(item_path, name)
    #     elif os.path.isfile(item_path):
    #         if name in item:
    #             global result
    #             result.append(item_path + ";")
    #             print(item_path + ";", end="")
    #
    # search(name, path=r"/home/tarena/sousuo")


@api.route("/download")
def show_download():
    # 根据文件的创建时间 默认展示10 条
    # 在数据库中查询
    try:
        # 获取10条信息 -- >并以列表方式呈现
        download = Download.order_by("create_time").limit(10).all()
        # time =download.create_time

    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="查询失败")

    data = []

    for elem in download:
        res.append(elem.file_name)
    # 返回文件名列表
    return jsonify(errno=RET.OK, errmsg="OK", data=data)

