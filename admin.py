from apscheduler.jobstores.base import JobLookupError
from flask import Blueprint, render_template, request, redirect, url_for, session, g

import mail
import models
from auth import admin_required
from models import YouthLeagueBranch, Subscription, SystemAdmin, day_of_week_dict
from app import db, scheduler
from branch import _update, _notify
import exceptions

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/members')
@admin_required
def members():
    return render_template('admin/members.html', branches=get_branches())


@admin_bp.route('/admin/update')
@admin_required
def update():
    branches = get_branches()
    for branch in branches:
        _update(branch.id)
    return redirect(url_for('admin.members'))


@admin_bp.route('/admin/notify')
@admin_required
def notify():
    branches = get_branches()
    for branch in branches:
        _notify(branch.id)
    return redirect(url_for('admin.members'))


@admin_bp.route('/admin/subscriptions')
@admin_required
def subscriptions():
    g.day_of_week_dict = models.display_day_of_week_dict
    return render_template('subscriptions.html', subscriptions=get_subscriptions())


@admin_bp.route('/admin/subscriptions/add', methods=['GET', 'POST'])
@admin_required
def add_subscription():
    if request.method == 'GET':
        return render_template('admin/add_subscription.html')
    else:
        subscription_name = request.form['subscription_name']
        day_of_week = request.form['weekday']
        tim = request.form['time']
        hour, minute = tim.split(':')
        # print(subscription_name, day_of_week, hour, minute)
        create_subscription(subscription_name, day_of_week[:3].lower(), hour, minute)
        return redirect(url_for('admin.subscriptions'))


@admin_bp.route('/admin/subscriptions/delete', methods=['GET', 'POST'])
@admin_required
def delete_subscription():
    g.day_of_week_dict = models.display_day_of_week_dict
    if request.method == 'GET':
        return render_template('admin/delete_subscription.html', subscriptions=get_subscriptions())
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _delete_subscription(key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


@admin_bp.route('/admin/subscriptions/enable', methods=['GET', 'POST'])
@admin_required
def enable_subscription():
    g.day_of_week_dict = models.display_day_of_week_dict
    if request.method == 'GET':
        return render_template('admin/enable_subscription.html', subscriptions=get_subscriptions())
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _enable_subscription(key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


@admin_bp.route('/admin/subscriptions/disable', methods=['GET', 'POST'])
@admin_required
def disable_subscription():
    g.day_of_week_dict = models.display_day_of_week_dict
    if request.method == 'GET':
        return render_template('admin/disable_subscription.html', subscriptions=get_subscriptions())
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _disable_subscription(key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


def create_subscription(subscription_name, day_of_week: str, hour: int, minute: int):
    subscription = Subscription(name=subscription_name,
                                day_of_week=day_of_week_dict[day_of_week],
                                hour=hour, minute=minute,
                                enabled=False)
    db.session.add(subscription)
    db.session.commit()
    # print('subscription added')
    return subscription.id


def _delete_subscription(subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    if subscription is not None:
        db.session.delete(subscription)
        db.session.commit()


# may throw exception
def _enable_subscription(subscription_id):
    # print(subscription_id)
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    if subscription is None:
        raise exceptions.SubscriptionNotFoundException()
    if subscription.enabled:
        return
    # print('subscription_id={}'.format(subscription_id))
    # print('day_of_week={}, hour={}, minute={}'.format(subscription.day_of_week, subscription.hour, subscription.minute))
    # updating_user_ids = [user.id for user in subscription.users if not user.studied]
    scheduler.add_job(func=execute_schedule, args=(subscription.id,), trigger='cron',
                      # week='*', year='*',
                      day_of_week=day_of_week_dict[subscription.day_of_week],
                      hour=subscription.hour, minute=subscription.minute,
                      id=subscription_id
                      )
    # print('added')
    subscription.enabled = True
    db.session.commit()


# may throw exception
def _disable_subscription(subscription_id):
    print(subscription_id)
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    if subscription is None:
        raise exceptions.SubscriptionNotFoundException()
    if not subscription.enabled:
        return
    try:
        scheduler.remove_job(subscription_id)
    except JobLookupError:
        pass
    subscription.enabled = False
    db.session.commit()


def get_subscriptions():
    return Subscription.query.all()


def get_branches():
    return SystemAdmin.query.filter_by(id=int(session['admin_id'])).first().youth_league_branches


# may throw exception
def execute_schedule(subscription_id):
    # with current_app.app_context():
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    updating_users = subscription.users
    branches = set()
    for user in updating_users:
        branches.add(user.youth_league_branch_id)
    updating_branches = subscription.branches
    for branch in updating_branches:
        branches.add(branch.id)

    for branch_id in branches:
        branch = YouthLeagueBranch.query.filter_by(id=branch_id).first()
        studied_list, unstudied_list = branch.update()

        cnt = 0
        for user in branch.users:
            print(user)
            if branch in updating_branches:
                print(branch)
                if user.real_name in studied_list:
                    print(user.finished)
                    if not user.finished:
                        user.finished = True
                        cnt += 1
                else:
                    mail.send_reminder(user.email_address, user.nickname, 12, 11)
            elif user in updating_users:
                if user.real_name in studied_list:
                    if not user.finished:
                        user.finished = True
                else:
                    mail.send_reminder(user.email_address, user.nickname, 12, 11)
        if branch in updating_branches:
            branch.num_finished += cnt
    db.session.commit()
