"""
Google OAuth Authentication
"""

from flask import Blueprint, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required
from app import db, oauth
from models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login")
def login():
    redirect_uri = url_for("auth.callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/callback")
def callback():
    token    = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo")

    if not userinfo:
        flash("Google login failed. Please try again.", "danger")
        return redirect(url_for("dashboard.index"))

    user = User.query.filter_by(google_id=userinfo["sub"]).first()
    if not user:
        user = User(
            google_id = userinfo["sub"],
            name      = userinfo.get("name", ""),
            email     = userinfo.get("email", ""),
            picture   = userinfo.get("picture", ""),
            role      = "admin" if userinfo.get("email") == "admin@nyakaglobal.org" else "staff",
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(f"Welcome, {user.name}!", "success")
    return redirect(url_for("dashboard.index"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("dashboard.index"))
