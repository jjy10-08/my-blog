#草稿

from . import api
# debug : loop import db
from ihub import db


@api.route("/index", methods=['GET'])
def index():
    return "heelellelelelel"
