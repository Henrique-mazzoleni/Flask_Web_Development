from flask import jsonify


from . import api
from .. import db
from ..models import User, Permission
from .errors import forbidden
from .decorators import permission_required

@api.route('/user/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json)
