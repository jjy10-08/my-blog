from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ihub import constants
from . import db


class BaseModel:
    create_time = db.Column(db.DateTime, default=datetime.now)  # create time
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseModel, db.Model):
    ''' ueser'''
    __tablename__ = 'th_user'

    id = db.Column(db.Integer, primary_key=True)  # user_id
    mobile = db.Column(db.Integer, unique=True, nullable=True)  # 手机号作为账号
    name = db.Column(db.String(32), unique=True, nullable=False)  # 昵称 默认为手机号
    password_hash = db.Column(db.String(128), nullable=False)  # plus scret password
    class_num = db.Column(db.String(64), default="")
    introduce = db.Column(db.String(256), default="")
    avatar_url = db.Column(db.String(128))

    @property
    def password(self):
        ''' when acquiring password  called it '''
        raise AttributeError('cannot read')

    @password.setter
    def password(self, passwd):
        ''' when  setting password called it and setting hash_pwd '''
        self.password_hash = generate_password_hash(passwd)

    def check_password(self, passwd):
        ''' check the psswd's correction
            检验密码的正确性
            正确返回TRUE 错误返回False
        '''
        return check_password_hash(self.password_hash, passwd)

    def to_dict(self):
        ''' change the obj to dic data '''
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "avatar_url": constants.QINIU_URL_PREFIX + self.avart_url if self.avart_url else "",
            "class_num": self.class_num,
            "introduce": self.introduce,
            "create_time": self.create_time.strftime("%Y-%m-%d  %H:%M:%S")
        }

        return user_dict



class Download(BaseModel, db.Model):
    __tablename__ = 'th_download'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(128), unique=True, nullable=False)
    describe = db.Column(db.String(256), nullable=False)
    url_path = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        info_dict = {
            "file_name": self.file_name,
            "describe": self.describe,
            "url_path": self.url_path,
            "create_time": self.create_time,
        }
        return info_dict


class Chatting(BaseModel, db.Model):
    __tablename__ = 'th_chatting'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256), nullable=False)
    auth = db.Column(db.String(128), nullable=False)  # 即昵称 name

    def update_content(self, new_info):
        self.content = new_info
        return self.content

    def to_dic(self):
        info_dict = {
            "content": self.content,
            "auth": self.auth,

        }
        return info_dict

    def sort(self):
        pass


class Query(BaseModel, db.Model):
    __tablename__ = 'th_querry'
    id = db.Column(db.Integer, primary_key=True)
    like = db.Column(db.Integer, default=0)
    chat_id = db.Column(db.Integer, db.ForeignKey('Chatting.id'))
    comment = db.Column(db.String(256))
    name = db.Column(db.String(128))
