from flask import Flask, render_template
from flask_login import LoginManager

from config import Config
from models import User, db
from routes.admin import admin_bp
from routes.ai_chat import ai_chat_bp
from routes.auth import auth_bp
from routes.user import user_bp


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

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_chat_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
