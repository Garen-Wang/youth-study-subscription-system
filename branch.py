from flask import Blueprint, render_template, session, redirect, url_for, flash, request, g
import datetime

from werkzeug.security import generate_password_hash

import mail
from app import db
import data_updater
from models import YouthLeagueBranch, User, YouthStudyEpisode, Subscription, day_of_week_dict
from auth import branch_required

branch = Blueprint('branch', __name__)


def get_league_members():
    return data_updater.get_member_list('secret/youth_league_member_list.xls')


@branch.before_request
def load_branch():
    if session['branch_id']:
        branch = YouthLeagueBranch.query.filter_by(id=session['branch_id']).first()
        g.branch = branch


@branch.route('/branch/members')
@branch_required
def members():
    g.finished_dict = {True: '是', False: '否'}
    # df = pd.DataFrame(columns=['id', 'real_name', 'finished'])
    assert branch
    # for user in branch.users:
    #     print(user)
        # df = df.append({'id': user.id, 'real_name': user.real_name, 'finished': user.finished}, ignore_index=True)
    return render_template('branch/members.html')


# update youth study status
@branch.route('/branch/update')
@branch_required
def update():
    _update(session['branch_id'])
    return redirect(url_for('branch.members'))


def _update(branch_id):
    branch = YouthLeagueBranch.query.filter_by(id=branch_id).first()
    studied_list = data_updater.update_studied_list()
    for real_name in studied_list:
        temp = User.query.filter_by(real_name=real_name, youth_league_branch_id=branch_id).first()
        if temp and temp.finished is False:
            temp.finished = True
            branch.num_finished += 1
    now = datetime.datetime.utcnow()
    User.query.filter_by(youth_league_branch_id=branch_id).update(dict(updated_at=now))
    branch.updated_at = now
    db.session.commit()


@branch.route('/branch/notify')
@branch_required
def notify():
    _notify(session['branch_id'])
    flash('sent emails to unfinished users')
    return redirect(url_for('branch.members'))


def _notify(branch_id):
    users = User.query.filter_by(youth_league_branch_id=branch_id, finished=False).all()
    for user in users:
        mail.send_reminder(user.email_address, user.nickname, 12, 11)


@branch.route('/branch/subscriptions')
@branch_required
def subscriptions():
    g.day_of_week_dict = day_of_week_dict
    return render_template('subscriptions.html', subscriptions=get_subscriptions(), branch=YouthLeagueBranch.query.filter_by(id=session['branch_id']).first())


@branch.route('/branch/subscribe', methods=['GET', 'POST'])
@branch_required
def subscribe():
    g.day_of_week_dict = day_of_week_dict
    if request.method == 'GET':
        return render_template('subscribe.html', subscriptions=get_subscriptions())
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _subscribe(session['branch_id'], key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


@branch.route('/branch/unsubscribe', methods=['GET', 'POST'])
@branch_required
def unsubscribe():
    g.day_of_week_dict = day_of_week_dict
    if request.method == 'GET':
        return render_template('unsubscribe.html', subscriptions=get_subscriptions())
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _unsubscribe(session['branch_id'], key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


@branch.route('/branch/user_register', methods=['GET', 'POST'])
@branch_required
def user_register():
    if request.method == 'GET':
        return render_template('branch/user_register.html')
    else:
        email_address = request.form.get('email')
        phone_number = request.form.get('phone')
        real_name = request.form.get('real_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        branch_id = session['branch_id']
        nickname = real_name

        if len(email_address) == 0 or len(phone_number) == 0 or len(real_name) == 0 or len(password) == 0 or len(confirm_password) == 0:
            flash('please fill out your form')
            return render_template('branch/user_register.html')
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


def _subscribe(branch_id, subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    branch = YouthLeagueBranch.query.filter_by(id=branch_id).first()
    subscription.branches.append(branch)
    db.session.commit()
    # print('subscribed')


def _unsubscribe(branch_id, subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    branch = YouthLeagueBranch.query.filter_by(id=branch_id).first()
    subscription.branches.remove(branch)
    db.session.commit()
    # print('unsubscribed')


def get_subscriptions():
    return Subscription.query.all()
