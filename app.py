import atexit
import json
import datetime

from flask import Flask, session, Response
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


def create_app():
    app = Flask(__name__)
    # app.config.from_object(config.Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = 'EDG_FLANDRE_JIEJIE_SCOUT_VIPER_MEIKO_S11_YYDS'
    app.config['SESSION_COOKIE_NAME'] = "session_key"
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=20)
    db.init_app(app)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.route('/session')
    def check_session():
        session_name = session['uname']
        print('session_name = {}'.format(session_name))
        return Response(json.dumps(session_name, ensure_ascii=False), mimetype='application/json')

    @app.route('/hello')
    def hello_world():
        return 'hello world'

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
