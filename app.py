"""
NYAKA GLOBAL ORGANIZATION - AI Platform
All extensions defined here to avoid any module-not-found issues.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

# Extensions — defined at module level so all files can import from here
db            = SQLAlchemy()
login_manager = LoginManager()
mail          = Mail()
oauth         = OAuth()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "nyaka-dev-secret-2024")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///nyaka.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAIL_SERVER"]   = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"]     = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"]  = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    # Import models so SQLAlchemy registers them
    from models import User, Student, Grandmother, SMSLog, SGBVReport  # noqa

    # Blueprints
    from routes.auth      import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.dropout   import dropout_bp
    from routes.sgbv      import sgbv_bp
    from routes.sms       import sms_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dropout_bp)
    app.register_blueprint(sgbv_bp)
    app.register_blueprint(sms_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    with app.app_context():
        db.create_all()
        from utils.seed import seed_sample_data
        seed_sample_data()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, port=5000)
