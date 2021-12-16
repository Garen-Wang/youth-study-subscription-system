from flask import Blueprint, render_template, session

from models import User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if 'user_id' in session.keys() and session['user_finished'] is False:
        user = User.query.filter_by(id=session['user_id']).first()
        if user.finished is True:
            session['user_finished'] = True
    return render_template('index.html')


@main.route('/profile')
def profile():
    return render_template('profile.html')
