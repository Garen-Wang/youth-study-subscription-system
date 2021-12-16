from flask import Blueprint, render_template, request, session, redirect, url_for

from app import db
from auth import user_required
from models import Subscription, User, YouthLeagueBranch

user = Blueprint('user', __name__)


@user.route('/user/update')
@user_required
def update():
    user = User.query.filter_by(id=session['user_id']).first()
    if user.finished is True:
        session['user_finished'] = True
        return redirect(url_for('main.index'))

    branch = YouthLeagueBranch.query.filter_by(id=session['branch_id']).first()
    studied_list, unstudied_list = branch.update()
    if session['user_real_name'] in studied_list and session['user_finished'] is False:
        user.finished = True
        branch.num_finished += 1
        session['user_finished'] = True
    return redirect(url_for('main.index'))


@user.route('/user/subscriptions')
@user_required
def subscriptions():
    return render_template('subscriptions.html', subscriptions=get_subscriptions())


@user.route('/user/subscribe', methods=['GET', 'POST'])
@user_required
def subscribe():
    if request.method == 'GET':
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('subscribe.html', subscriptions=get_subscriptions(), user=user)
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _subscribe(session['user_id'], key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


@user.route('/user/unsubscribe', methods=['GET', 'POST'])
@user_required
def unsubscribe():
    if request.method == 'GET':
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('unsubscribe.html', subscriptions=get_subscriptions(), user=user)
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _unsubscribe(session['user_id'], key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


def get_subscriptions():
    return Subscription.query.all()


def _subscribe(user_id, subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    user = User.query.filter_by(id=user_id).first()
    subscription.users.append(user)
    db.session.commit()
    print('subscribed')


def _unsubscribe(user_id, subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    user = User.query.filter_by(id=user_id).first()
    subscription.users.remove(user)
    db.session.commit()
    print('unsubscribed')
