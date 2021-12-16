from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import datetime
import mail
from app import db
import data_updater
from models import YouthLeagueBranch, User, YouthStudyEpisode, Subscription
from auth import branch_required

branch = Blueprint('branch', __name__)


def get_league_members():
    return data_updater.get_member_list('secret/youth_league_member_list.xls')


@branch.route('/branch/members')
@branch_required
def members():
    branch = YouthLeagueBranch.query.filter_by(id=session['branch_id']).first()
    # df = pd.DataFrame(columns=['id', 'real_name', 'finished'])
    assert branch
    # for user in branch.users:
    #     print(user)
        # df = df.append({'id': user.id, 'real_name': user.real_name, 'finished': user.finished}, ignore_index=True)
    return render_template('branch/members.html', users=branch.users)


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
    return render_template('subscriptions.html', subscriptions=get_subscriptions())


@branch.route('/branch/subscribe', methods=['GET', 'POST'])
@branch_required
def subscribe():
    if request.method == 'GET':
        branch = YouthLeagueBranch.query.filter_by(id=session['branch_id']).first()
        return render_template('subscribe.html', subscriptions=get_subscriptions(), branch=branch)
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _subscribe(session['branch_id'], key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


@branch.route('/branch/unsubscribe', methods=['GET', 'POST'])
@branch_required
def unsubscribe():
    if request.method == 'GET':
        branch = YouthLeagueBranch.query.filter_by(id=session['branch_id']).first()
        return render_template('unsubscribe.html', subscriptions=get_subscriptions(), branch=branch)
    else:
        for key in request.form:
            if request.form[key] == 'on':
                _unsubscribe(session['branch_id'], key[12:])
        return render_template('subscriptions.html', subscriptions=get_subscriptions())


def _subscribe(branch_id, subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    branch = YouthLeagueBranch.query.filter_by(id=branch_id).first()
    subscription.branches.append(branch)
    db.session.commit()
    print('subscribed')


def _unsubscribe(branch_id, subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    branch = YouthLeagueBranch.query.filter_by(id=branch_id).first()
    subscription.branches.remove(branch)
    db.session.commit()
    print('unsubscribed')


def get_subscriptions():
    return Subscription.query.all()
