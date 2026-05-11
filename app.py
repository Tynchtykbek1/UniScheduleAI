from flask import Flask
from flask_login import LoginManager

from config import Config
from models import User, db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    try:
        from routes.auth import auth_bp

        app.register_blueprint(auth_bp)
    except ImportError:
        pass

    try:
        from routes.user import user_bp

        app.register_blueprint(user_bp)
    except ImportError:
        pass

    try:
        from routes.admin import admin_bp

        app.register_blueprint(admin_bp)
    except ImportError:
        pass

    try:
        from routes.ai_chat import ai_chat_bp

        app.register_blueprint(ai_chat_bp)
    except ImportError:
        pass

    @app.route("/")
    def index():
        return "UniSchedule AI is running. Routes will be added in later steps."

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
