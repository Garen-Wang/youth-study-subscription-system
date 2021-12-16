import atexit
import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, logging
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config.from_object(config.Config)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'example_secret_key'
app.config['SESSION_COOKIE_NAME'] = "session_key"
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=20)
app.app_context().push()
db = SQLAlchemy(app, session_options={
    'expire_on_commit': False
})
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

logger = logging.create_logger(app)

from auth import auth_bp as auth_blueprint
app.register_blueprint(auth_blueprint)

from index import index_bp as index_blueprint
app.register_blueprint(index_blueprint)

from user import user_bp as user_blueprint
app.register_blueprint(user_blueprint)

from branch import branch_bp as branch_blueprint
app.register_blueprint(branch_blueprint)

from admin import admin_bp as admin_blueprint
app.register_blueprint(admin_blueprint)

atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run()
