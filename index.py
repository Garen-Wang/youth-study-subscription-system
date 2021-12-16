from flask import Blueprint, render_template, session, g

from models import User

index_bp = Blueprint('index', __name__)


@index_bp.before_request
def load_dicts():
    role_dict = {1: '用户', 2: '团支部', 3: '系统管理员'}
    g.role_dict = role_dict


@index_bp.route('/')
def index():
    if 'user_id' in session.keys() and session['user_finished'] is False:
        user = User.query.filter_by(id=session['user_id']).first()
        if user.finished is True:
            session['user_finished'] = True
    return render_template('index.html')

