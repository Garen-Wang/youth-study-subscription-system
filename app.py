import atexit
import json
import datetime

from flask import Flask, logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy

# import mail
# from models import Subscription, YouthLeagueBranch

# db = SQLAlchemy()
# scheduler = BackgroundScheduler(daemon=True)
# atexit.register(lambda: scheduler.shutdown())

# def create_app():
#     app = Flask(__name__)
#     # app.config.from_object(config.Config)
#     app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite"
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#     app.config['SECRET_KEY'] = 'EDG_FLANDRE_JIEJIE_SCOUT_VIPER_MEIKO_S11_YYDS'
#     app.config['SESSION_COOKIE_NAME'] = "session_key"
#     app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=20)
#     db.init_app(app)
#     # scheduler.init_app(app)
#     scheduler.start()
#
#     from auth import auth as auth_blueprint
#     app.register_blueprint(auth_blueprint)
#
#     from main import main as main_blueprint
#     app.register_blueprint(main_blueprint)
#
#     from user import user as user_blueprint
#     app.register_blueprint(user_blueprint)
#
#     from branch import branch as branch_blueprint
#     app.register_blueprint(branch_blueprint)
#
#     from admin import admin as admin_blueprint
#     app.register_blueprint(admin_blueprint)
#
#     @app.route('/session')
#     def check_session():
#         session_name = session['branch_id']
#         print('session_name = {}'.format(session_name))
#         return Response(json.dumps(session_name, ensure_ascii=False), mimetype='application/json')
#
#     @app.route('/hello')
#     def hello_world():
#         return 'hello world'
#
#     return app
#
#
# if __name__ == '__main__':
#     app = create_app()
#     app.run()
#     app.app_context().push()


# scheduler = BackgroundScheduler()
# atexit.register(lambda: scheduler.shutdown())

# def create_app():
#     app = Flask(__name__)
#     # app.config.from_object(config.Config)
#     app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite"
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#     app.config['SECRET_KEY'] = 'EDG_FLANDRE_JIEJIE_SCOUT_VIPER_MEIKO_S11_YYDS'
#     app.config['SESSION_COOKIE_NAME'] = "session_key"
#     app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=20)
#     db.init_app(app)
#     # scheduler.init_app(app)
#     scheduler.start()
#
#     from auth import auth as auth_blueprint
#     app.register_blueprint(auth_blueprint)
#
#     from main import main as main_blueprint
#     app.register_blueprint(main_blueprint)
#
#     from user import user as user_blueprint
#     app.register_blueprint(user_blueprint)
#
#     from branch import branch as branch_blueprint
#     app.register_blueprint(branch_blueprint)
#
#     from admin import admin as admin_blueprint
#     app.register_blueprint(admin_blueprint)
#
#     @app.route('/session')
#     def check_session():
#         session_name = session['branch_id']
#         print('session_name = {}'.format(session_name))
#         return Response(json.dumps(session_name, ensure_ascii=False), mimetype='application/json')
#
#     @app.route('/hello')
#     def hello_world():
#         return 'hello world'
#
#     return app
#
#
# if __name__ == '__main__':
#     app = create_app()
#     app.run()
#     app.app_context().push()

atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)
# app.config.from_object(config.Config)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'EDG_FLANDRE_JIEJIE_SCOUT_VIPER_MEIKO_S11_YYDS'
app.config['SESSION_COOKIE_NAME'] = "session_key"
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=20)
app.app_context().push()
db = SQLAlchemy(app, session_options={
    'expire_on_commit': False
})
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

logger = logging.create_logger(app)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from main import main as main_blueprint
app.register_blueprint(main_blueprint)

from user import user as user_blueprint
app.register_blueprint(user_blueprint)

from branch import branch as branch_blueprint
app.register_blueprint(branch_blueprint)

from admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint)


@app.route('/hello')
def hello_world():
    return 'hello world'


if __name__ == '__main__':
    app.run()

