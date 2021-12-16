import datetime

from flask import current_app

import config
import data_updater
import mail
from app import db


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True)
    users = db.relationship('User', backref='role', lazy=True)

    # by default:
    # league members: 1
    # youth league branch admin: 2
    # system admin: 3

    def __repr__(self):
        return '<Role %r>' % self.name


subscriptions1 = db.Table(
    'subscriptions1',
    db.Column('subscription_id', db.Integer, db.ForeignKey('subscription.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


# league members and league branch secretaries are *Users* here
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    nickname = db.Column(db.String(20), unique=False, nullable=False)
    real_name = db.Column(db.String(20), unique=True, nullable=False)
    phone_number = db.Column(db.String(11), unique=False, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    finished = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    tags = db.relationship('Subscription', secondary=subscriptions1, lazy='subquery', backref=db.backref('users', lazy=True))

    # role id = 1
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    youth_league_branch_id = db.Column(db.Integer, db.ForeignKey('youth_league_branch.id'), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.real_name


subscriptions2 = db.Table(
    'subscriptions2',
    db.Column('subscription_id', db.Integer, db.ForeignKey('subscription.id'), primary_key=True),
    db.Column('branch_id', db.Integer, db.ForeignKey('youth_league_branch.id'), primary_key=True)
)


# cannot be registered directly
# can only be created by system admin
# youth league branch secretary has identity at user, and has another account for managing the branch
class YouthLeagueBranch(db.Model):
    __tablename__ = 'youth_league_branch'
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', backref='youth_league_branch', lazy=True)

    real_name = db.Column(db.String(20), unique=True, nullable=False)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(11), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    num_finished = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    tags = db.relationship('Subscription', secondary=subscriptions2, lazy='subquery', backref=db.backref('branches', lazy=True))

    # role id = 2
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('system_admin.id'), nullable=False)

    login_link = db.Column(db.String(400), default=config.login_link)
    data_link = db.Column(db.String(400), default=config.data_link)

    def update(self):
        updater = data_updater.DataUpdater(self.login_link, self.data_link)
        updater.run()
        return list(updater.studied_name_list), list(updater.unstudied_name_list)


# only the admin can log in and see the backend
# there exists only one admin
class SystemAdmin(db.Model):
    __tablename__ = 'system_admin'
    id = db.Column(db.Integer, primary_key=True)

    real_name = db.Column(db.String(20), unique=True, nullable=False)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(11), unique=False, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # role id = 3
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    youth_league_branches = db.relationship('YouthLeagueBranch', backref='admin', lazy=True)

    def __repr__(self):
        return '<Admin %r>' % self.nickname


class YouthStudyEpisode(db.Model):
    __tablename__ = 'youth_study_episode'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)

    season = db.Column(db.Integer, nullable=False)
    special = db.Column(db.Boolean, nullable=False, default=False)
    episode = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow())

    def __repr__(self):
        if self.special:
            return '<YouthStudy Season %r Special Episode %r>' % (self.season, self.episode)
        else:
            return '<YouthStudy Season %r Episode %r>' % (self.season, self.episode)


class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    day_of_week = db.Column(db.Integer, default=2)
    hour = db.Column(db.Integer, default=8)
    minute = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Subscription %r>' % self.name


day_of_week_dict = {
    # used for cron trigger
    'sun': 0,
    'mon': 1,
    'tue': 2,
    'wed': 3,
    'thu': 4,
    'fri': 5,
    'sat': 6,
    0: 'sun',
    1: 'mon',
    2: 'tue',
    3: 'wed',
    4: 'thu',
    5: 'fri',
    6: 'sat',
}

display_day_of_week_dict = {
    0: '星期日',
    1: '星期一',
    2: '星期二',
    3: '星期三',
    4: '星期四',
    5: '星期五',
    6: '星期六',
    '星期日': 0,
    '星期一': 1,
    '星期二': 2,
    '星期三': 3,
    '星期四': 4,
    '星期五': 5,
    '星期六': 6,
}
