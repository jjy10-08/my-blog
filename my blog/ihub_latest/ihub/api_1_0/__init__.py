from flask import Blueprint

# create object of BluePrint

api = Blueprint("api_1_0", __name__)

# import blueprint 's views func

from . import  verify_code,password,profile,search,chat,download,draft
