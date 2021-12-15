import functools
import time

from flask import Blueprint, request, render_template, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

import config
import mail
import ver
from models import User
from app import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        account = request.form.get('account')
        password = request.form.get('password')

        if len(account) == 0:
            flash('account cannot be null')
            return redirect(request.url)
        elif not password or len(password) == 0:
            flash('password cannot be null')
            return render_template('login.html')

        user = None
        if '@' in account:
            user = User.query.filter_by(email_address=account).first()
        elif account.isdigit():
            user = User.query.filter_by(phone_number=account).first()
        else:
            user = User.query.filter_by(real_name=account).first()
        if not user:
            flash('cannot find user')
            return redirect(request.url)

        if check_password_hash(user.password_hash, password):
            # TODO: magic state for server to authenticate
            # g.logged_in_status[user.id] = "{}_{}_LOGGED_IN".format(time.time(), user.email_address)
            # session['magic'] = g.logged_in_status[user.id]

            session['user_id'] = user.id
            session['user_email_address'] = user.email_address
            session['user_nickname'] = user.nickname
            session['user_real_name'] = user.real_name
            session['user_phone_number'] = user.phone_number
            session['user_finished'] = user.finished
            session['user_role_id'] = user.role_id
            session['user_youth_league_branch_id'] = user.youth_league_branch_id
            return redirect(url_for('main.index'))
        else:
            flash('incorrect password')
            return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if not config.registration_closed:
            return render_template('register.html')
        else:
            return render_template('error.html', error='Registration Closed',
                                   info='Registration has been closed temporarily by system admin.')
    else:
        if request.form.get('action') == 'Send':
            email_address = request.form.get('email')
            if not email_address or len(email_address) == 0:
                return redirect(url_for('auth.register'))
            mail.send_verification_code(email_address)
            return render_template('register.html')
        elif request.form.get('action') == 'Register':
            email_address = request.form.get('email')
            phone_number = request.form.get('phone')
            real_name = request.form.get('real_name')
            nickname = request.form.get('nickname')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            ver_code = request.form.get('ver_code')

            if len(email_address) == 0 or len(phone_number) == 0 or len(real_name) == 0 or len(password) == 0 or len(confirm_password) == 0:
                flash('please fill out your form')
                return render_template('register.html')
            # determine whether is empty

            temp = User.query.filter_by(email_address=email_address).first()
            if temp is not None:
                flash('email address already existed')
                return render_template('register.html')

            temp = User.query.filter_by(phone_number=phone_number).first()
            if temp is not None:
                flash('phone number already existed')
                return render_template('register.html')

            temp = User.query.filter_by(real_name=real_name).first()
            if temp is not None:
                flash('real name already existed')
                return render_template('register.html')

            if password != confirm_password:
                flash('your password is not the same')
                return render_template('register.html')

            if len(nickname) == 0:
                nickname = real_name

            if not ver.verify(email_address, ver_code):
                flash('wrong verification code')
                return render_template('register.html')

            user = User(
                email_address=email_address,
                nickname=nickname,
                real_name=real_name,
                phone_number=phone_number,
                password_hash=generate_password_hash(password),
                # TODO: role_id can be changed
                role_id=1,
                # TODO: youth_league_branch_id can also be changed
                youth_league_branch_id=1
            )
            db.session.add(user)
            db.session.commit()
            flash('registered')
            return redirect(request.url)
        else:
            return render_template('error.html', error='Unknown action',
                                   info='The action name is neither Send nor Register.')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session['user_id'] is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
