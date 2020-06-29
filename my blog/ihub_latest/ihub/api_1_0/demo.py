# GET 127.0.0.1:5000/api/v1.0/sms_codes/<mobile>
# @api.route("/sms_code/<re(r'1[34578]\d{9}'):mobile>")
# def get_sms_code(mobile):
#     '''
#     获取短信验证码 get
#     '''
#     # 获取参数
#     image_code = request.args.get('image_code')
#     image_code_id = request.args.get('image_code_id')
#     # 校验参数
#     if not all([image_code_id, image_code]):




# # 加载信息接口
# @api.route("/user", methods=["GET"])
# @login_required
# def show_profile():
#     '''获取个人信息
#     :return:
#     '''
#     # g.user_id
#     # 查询数据库获取个人信息
#     pass
