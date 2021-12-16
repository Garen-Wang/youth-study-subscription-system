import functools

from flask import Blueprint, request, render_template, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from config import user_registration_closed, admin_registration_closed, branch_registration_closed
import mail
import ver
from models import User, SystemAdmin, YouthLeagueBranch
from app import db

auth_bp = Blueprint('auth', __name__)


def not_logged_in_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' in session.keys() or 'branch_id' in session.keys() or 'admin_id' in session.keys():
            return redirect(url_for('index.index'))
        return view(**kwargs)
    return wrapped_view


def user_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session.keys() or session['user_id'] is None or 'role_id' not in session.keys() or session['role_id'] != 1:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def branch_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'branch_id' not in session.keys() or session['branch_id'] is None or 'role_id' not in session.keys() or session['role_id'] != 2:
            return render_template('error.html', error='没有权限操作',
                                   info='当前账号没有团支部权限'), 404
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'admin_id' not in session.keys() or session['admin_id'] is None or 'role_id' not in session.keys() or session['role_id'] != 3:
            return render_template('error.html', error='没有权限操作',
                                   info='当前账号没有系统管理员权限'), 404
        return view(**kwargs)
    return wrapped_view


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
@not_logged_in_required
def admin_login():
    if request.method == 'GET':
        return render_template('auth/admin_login.html')
    else:
        account = request.form.get('account')
        password = request.form.get('password')
        if len(account) == 0:
            flash('account cannot be null')
            return redirect(request.url)
        elif not password or len(password) == 0:
            flash('password cannot be null')
            return render_template('auth/admin_login.html')

        admin = None
        if '@' in account:
            admin = SystemAdmin.query.filter_by(email_address=account).first()
        elif account.isdigit():
            admin = SystemAdmin.query.filter_by(phone_number=account).first()
        if not admin:
            flash('cannot find admin')
            return redirect(request.url)

        if check_password_hash(admin.password_hash, password):

            # g.logged_in_status[user.id] = "{}_{}_LOGGED_IN".format(time.time(), user.email_address)
            # session['magic'] = g.logged_in_status[user.id]
            session.clear()
            session['admin_id'] = admin.id
            session['admin_email_address'] = admin.email_address
            session['admin_real_name'] = admin.real_name
            session['admin_phone_number'] = admin.phone_number
            session['role_id'] = admin.role_id
            return redirect(url_for('index.index'))
        else:
            flash('incorrect password')
            return render_template('login.html')


@auth_bp.route('/branch/login', methods=['GET', 'POST'])
@not_logged_in_required
def branch_login():
    if request.method == 'GET':
        return render_template('auth/branch_login.html')
    else:
        account = request.form.get('account')
        password = request.form.get('password')
        if len(account) == 0:
            flash('account cannot be null')
            return redirect(request.url)
        elif not password or len(password) == 0:
            flash('password cannot be null')
            return render_template('auth/branch_login.html')

        branch = None
        if '@' in account:
            branch = YouthLeagueBranch.query.filter_by(email_address=account).first()
        elif account.isdigit():
            branch = YouthLeagueBranch.query.filter_by(phone_number=account).first()
        if not branch:
            flash('cannot find branch')
            return redirect(request.url)

        if check_password_hash(branch.password_hash, password):
            # g.logged_in_status[user.id] = "{}_{}_LOGGED_IN".format(time.time(), user.email_address)
            # session['magic'] = g.logged_in_status[user.id]

            session.clear()
            session['branch_id'] = branch.id
            session['branch_email_address'] = branch.email_address
            session['branch_real_name'] = branch.real_name
            session['branch_phone_number'] = branch.phone_number
            session['role_id'] = branch.role_id
            session['admin_id'] = branch.admin_id
            return redirect(url_for('index.index'))
        else:
            flash('incorrect password')
            return render_template('auth/branch_login.html')


@auth_bp.route('/user/login', methods=['GET', 'POST'])
@not_logged_in_required
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
        if not user:
            flash('cannot find user')
            return redirect(request.url)

        if check_password_hash(user.password_hash, password):
            # TODO: magic state for server to authenticate
            # g.logged_in_status[user.id] = "{}_{}_LOGGED_IN".format(time.time(), user.email_address)
            # session['magic'] = g.logged_in_status[user.id]

            session.clear()
            session['user_id'] = user.id
            session['user_email_address'] = user.email_address
            session['user_nickname'] = user.nickname
            session['user_real_name'] = user.real_name
            session['user_phone_number'] = user.phone_number
            session['user_finished'] = user.finished
            session['role_id'] = user.role_id
            session['branch_id'] = user.youth_league_branch_id
            return redirect(url_for('index.index'))
        else:
            flash('incorrect password')
            return render_template('login.html')


@auth_bp.route('/admin/register', methods=['GET', 'POST'])
@not_logged_in_required
def admin_register():
    if request.method == 'GET':
        if not admin_registration_closed:
            return render_template('auth/admin_register.html')
        else:
            return render_template('error.html', error='Registration Closed',
                                   info='Registration has been closed temporarily by system admin'), 404
    else:
        if admin_registration_closed:
            return render_template('error.html', error='Registration Closed',
                                   info='Registration has been closed temporarily by system admin'), 404
        if request.form.get('action') == '发送':
            email_address = request.form.get('email')
            if not email_address or len(email_address) == 0:
                return redirect(url_for('auth.admin_register'))
            mail.send_verification_code(email_address)
            return render_template('auth/admin_register.html')
        elif request.form.get('action') == '注册':
            email_address = request.form.get('email')
            phone_number = request.form.get('phone')
            real_name = request.form.get('real_name')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            ver_code = request.form.get('ver_code')

            if len(email_address) == 0 or len(phone_number) == 0 or len(real_name) == 0 or len(password) == 0 or len(confirm_password) == 0:
                flash('please fill out your form')
                return render_template('auth/admin_register.html')
            # determine whether is empty

            temp = SystemAdmin.query.filter_by(email_address=email_address).first()
            if temp is not None:
                flash('email address already existed')
                return render_template('auth/admin_login.html')

            temp = SystemAdmin.query.filter_by(phone_number=phone_number).first()
            if temp is not None:
                flash('phone number already existed')
                return render_template('auth/admin_register.html')

            temp = SystemAdmin.query.filter_by(real_name=real_name).first()
            if temp is not None:
                flash('real name already existed')
                return render_template('auth/admin_register.html')

            if password != confirm_password:
                flash('your password is not the same')
                return render_template('auth/admin_register.html')

            if not ver.verify(email_address, ver_code):
                flash('wrong verification code')
                return render_template('auth/admin_register.html')

            admin = SystemAdmin(
                email_address=email_address,
                real_name=real_name,
                phone_number=phone_number,
                password_hash=generate_password_hash(password),
                role_id=3
            )
            db.session.add(admin)
            db.session.commit()
            flash('registered')
            return redirect(request.url)
        else:
            return render_template('error.html', error='Unknown action',
                                   info='The action name is neither Send nor Register.')


@auth_bp.route('/branch/register', methods=['GET', 'POST'])
@admin_required
def branch_register():
    if request.method == 'GET':
        if not branch_registration_closed:
            return render_template('auth/branch_register.html')
        else:
            return render_template('error.html', error='Registration Closed',
                                   info='Registration has been closed temporarily by system admin')
    else:
        if branch_registration_closed:
            return render_template('error.html', error='Registration Closed',
                                   info='Registration has been closed temporarily by system admin')
        if request.form.get('action') == '发送':
            email_address = request.form.get('email')
            if not email_address or len(email_address) == 0:
                return redirect(url_for('auth.branch_register'))
            mail.send_verification_code(email_address)
            return render_template('auth/branch_register.html')
        elif request.form.get('action') == '注册':
            email_address = request.form.get('email')
            phone_number = request.form.get('phone')
            real_name = request.form.get('real_name')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            ver_code = request.form.get('ver_code')

            if len(email_address) == 0 or len(phone_number) == 0 or len(real_name) == 0 or len(password) == 0 or len(confirm_password) == 0:
                flash('please fill out your form')
                return render_template('auth/branch_register.html')
            # determine whether is empty

            temp = YouthLeagueBranch.query.filter_by(email_address=email_address).first()
            if temp is not None:
                flash('email address already existed')
                return render_template('auth/branch_login.html')

            temp = YouthLeagueBranch.query.filter_by(phone_number=phone_number).first()
            if temp is not None:
                flash('phone number already existed')
                return render_template('auth/branch_register.html')

            temp = YouthLeagueBranch.query.filter_by(real_name=real_name).first()
            if temp is not None:
                flash('real name already existed')
                return render_template('auth/branch_register.html')

            if password != confirm_password:
                flash('your password is not the same')
                return render_template('auth/branch_register.html')

            if not ver.verify(email_address, ver_code):
                flash('wrong verification code')
                return render_template('auth/branch_register.html')

            branch = YouthLeagueBranch(
                email_address=email_address,
                real_name=real_name,
                phone_number=phone_number,
                password_hash=generate_password_hash(password),
                role_id=2,
                admin_id=session['admin_id']
            )
            db.session.add(branch)
            db.session.commit()
            flash('registered')
            return redirect(request.url)
        else:
            return render_template('error.html', error='Unknown action',
                                   info='The action name is neither Send nor Register.')


@auth_bp.route('/user/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if not user_registration_closed:
            return render_template('register.html')
        else:
            return render_template('error.html', error='注册渠道关闭',
                                   info='注册渠道已被系统管理员关闭')
    else:
        if user_registration_closed:
            return render_template('error.html', error='注册渠道关闭',
                                   info='注册渠道已被系统管理员关闭')

        if request.form.get('action') == '发送':
            email_address = request.form.get('email')
            if not email_address or len(email_address) == 0:
                return redirect(url_for('auth.register'))
            mail.send_verification_code(email_address)
            return render_template('register.html')
        elif request.form.get('action') == '注册':
            email_address = request.form.get('email')
            phone_number = request.form.get('phone')
            branch_id = request.form.get('branch_id')
            real_name = request.form.get('real_name')
            nickname = request.form.get('nickname')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            ver_code = request.form.get('ver_code')

            if len(email_address) == 0 or len(phone_number) == 0 or len(real_name) == 0 or len(password) == 0 or len(confirm_password) == 0 or len(branch_id) == 0:
                flash('please fill out your form')
                return render_template('register.html')
            # determine whether is empty

            temp = YouthLeagueBranch.query.filter_by(id=int(branch_id)).first()
            if temp is None:
                flash('branch id does not exist')
                return render_template('register.html')

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
                role_id=1,
                youth_league_branch_id=int(branch_id)
            )
            db.session.add(user)
            db.session.commit()
            flash('registered')
            return redirect(request.url)
        else:
            return render_template('error.html', error='Unknown action',
                                   info='The action name is neither Send nor Register.')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index.index'))

