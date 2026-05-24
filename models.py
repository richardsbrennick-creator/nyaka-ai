"""
Database models — imports db from extensions, not from app.
"""
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    google_id  = db.Column(db.String(128), unique=True, nullable=False)
    name       = db.Column(db.String(128))
    email      = db.Column(db.String(128), unique=True, nullable=False)
    picture    = db.Column(db.String(256))
    role       = db.Column(db.String(32), default="staff")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_admin(self):
        return self.role == "admin"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Student(db.Model):
    __tablename__ = "students"
    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(128), nullable=False)
    age              = db.Column(db.Integer)
    gender           = db.Column(db.String(16))
    grade            = db.Column(db.String(16))
    district         = db.Column(db.String(64))
    school           = db.Column(db.String(128))
    attendance_pct   = db.Column(db.Float, default=100.0)
    avg_grade_score  = db.Column(db.Float, default=70.0)
    meals_per_day    = db.Column(db.Float, default=2.0)
    distance_km      = db.Column(db.Float, default=1.0)
    has_both_parents = db.Column(db.Boolean, default=False)
    caregiver_is_gm  = db.Column(db.Boolean, default=True)
    num_siblings     = db.Column(db.Integer, default=3)
    prev_dropout     = db.Column(db.Boolean, default=False)
    dropout_risk     = db.Column(db.Float, default=0.0)
    risk_label       = db.Column(db.String(16), default="Low")
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    grandmother_phone= db.Column(db.String(32))


class Grandmother(db.Model):
    __tablename__ = "grandmothers"
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(128))
    phone        = db.Column(db.String(32), nullable=False)
    district     = db.Column(db.String(64))
    group_name   = db.Column(db.String(128))
    num_children = db.Column(db.Integer, default=1)
    language     = db.Column(db.String(32), default="English")
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)


class SMSLog(db.Model):
    __tablename__ = "sms_logs"
    id        = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(32))
    message   = db.Column(db.Text)
    category  = db.Column(db.String(64))
    status    = db.Column(db.String(32), default="pending")
    sent_at   = db.Column(db.DateTime, default=datetime.utcnow)


class SGBVReport(db.Model):
    __tablename__ = "sgbv_reports"
    id               = db.Column(db.Integer, primary_key=True)
    report_code      = db.Column(db.String(16), unique=True)
    incident_type    = db.Column(db.String(128))
    description      = db.Column(db.Text)
    location         = db.Column(db.String(128))
    district         = db.Column(db.String(64))
    victim_age_range = db.Column(db.String(32))
    victim_gender    = db.Column(db.String(32))
    relationship     = db.Column(db.String(64))
    urgent           = db.Column(db.Boolean, default=False)
    status           = db.Column(db.String(32), default="new")
    submitted_at     = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by      = db.Column(db.String(128))
    notes            = db.Column(db.Text)
