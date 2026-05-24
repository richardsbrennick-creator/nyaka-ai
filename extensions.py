"""
Flask extensions — initialized here to avoid circular imports.
Import these in app.py and models.py instead of importing from each other.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

db            = SQLAlchemy()
login_manager = LoginManager()
mail          = Mail()
oauth         = OAuth()
