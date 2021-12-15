from app import db


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True)
    users = db.relationship('User', backref='role', lazy=True)

    # by default:
    # league members: 1
    # tuan zhi shu: 2
    # youth league branch admin: 3
    # system admin: 4

    def __repr__(self):
        return '<Role %r>' % self.name


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

    # role id = 1 or 2
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    youth_league_branch_id = db.Column(db.Integer, db.ForeignKey('youth_league_branch.id'), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.real_name


class YouthLeagueBranch(db.Model):
    __tablename__ = 'youth_league_branch'
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', backref='youth_league_branch', lazy=True)
    # TODO: how to get total number of users?

    email_address = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(11), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    num_finished = db.Column(db.Integer, default=0, nullable=False)

    # role id = 3
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('system_admin.id'), nullable=False)


# only the admin can log in and see the backend
class SystemAdmin(db.Model):
    __tablename__ = 'system_admin'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(20), unique=False, nullable=False)
    league_branch_id = db.Column(db.String(100), unique=True, nullable=False)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(11), unique=False, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # role id = 4
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

    def __repr__(self):
        if self.special:
            return '<YouthStudy Season %r Special Episode %r>' % (self.season, self.episode)
        else:
            return '<YouthStudy Season %r Episode %r>' % (self.season, self.episode)


