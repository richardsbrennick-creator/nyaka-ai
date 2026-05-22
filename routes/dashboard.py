"""
Main Dashboard Route
"""

from flask import Blueprint, render_template
from flask_login import login_required
from models import Student, Grandmother, SGBVReport, SMSLog
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    # ── Summary stats ─────────────────────────────────────────────────────────
    total_students   = Student.query.count()
    total_gms        = Grandmother.query.count()
    high_risk        = Student.query.filter_by(risk_label="High").count()
    medium_risk      = Student.query.filter_by(risk_label="Medium").count()
    low_risk         = Student.query.filter_by(risk_label="Low").count()
    sgbv_new         = SGBVReport.query.filter_by(status="new").count()
    sms_sent         = SMSLog.query.filter_by(status="Success").count()

    # ── Recent high-risk students ─────────────────────────────────────────────
    at_risk_students = (
        Student.query
        .filter(Student.risk_label.in_(["High", "Medium"]))
        .order_by(Student.dropout_risk.desc())
        .limit(10)
        .all()
    )

    # ── District breakdown ────────────────────────────────────────────────────
    district_data = (
        db_session_query(Student, "district")
    )

    # ── Risk distribution by school ───────────────────────────────────────────
    school_risk = {}
    for school in ["Nyaka Primary School", "Kutamba Primary School", "Nyaka Secondary School"]:
        school_risk[school] = {
            "High":   Student.query.filter_by(school=school, risk_label="High").count(),
            "Medium": Student.query.filter_by(school=school, risk_label="Medium").count(),
            "Low":    Student.query.filter_by(school=school, risk_label="Low").count(),
        }

    # ── Recent SGBV reports ───────────────────────────────────────────────────
    recent_sgbv = SGBVReport.query.order_by(SGBVReport.submitted_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_students   = total_students,
        total_gms        = total_gms,
        high_risk        = high_risk,
        medium_risk      = medium_risk,
        low_risk         = low_risk,
        sgbv_new         = sgbv_new,
        sms_sent         = sms_sent,
        at_risk_students = at_risk_students,
        school_risk      = school_risk,
        recent_sgbv      = recent_sgbv,
    )


def db_session_query(model, field):
    """Helper to avoid importing db in routes."""
    from app import db
    return db.session.query(
        getattr(model, field),
        func.count(model.id)
    ).group_by(getattr(model, field)).all()
