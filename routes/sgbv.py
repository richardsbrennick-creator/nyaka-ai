"""
SGBV Anonymous Reporting Routes
"""

import random
import string
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from models import SGBVReport
from app import db, mail
import os

sgbv_bp = Blueprint("sgbv", __name__, url_prefix="/sgbv")

INCIDENT_TYPES = [
    "Sexual Violence",
    "Physical Violence",
    "Emotional / Psychological Abuse",
    "Child Marriage",
    "Female Genital Mutilation (FGM)",
    "Neglect / Abandonment",
    "Economic Abuse",
    "Other",
]

DISTRICTS = ["Rukungiri", "Kanungu", "Kihihi", "Nyakagyezi", "Other"]
AGE_RANGES = ["Under 10", "10-14", "15-17", "18-24", "25-34", "35+", "Unknown"]
RELATIONSHIPS = [
    "Parent / Guardian", "Relative", "Teacher", "Neighbor",
    "Stranger", "Partner / Spouse", "Unknown", "Other"
]


def _generate_code():
    """Generate a random anonymous reference code."""
    return "NYK-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def _notify_admin(report: SGBVReport):
    """Email admin about new SGBV report."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@nyakaglobal.org")
    try:
        msg = Message(
            subject  = f"[URGENT] New SGBV Report #{report.report_code} - Nyaka AI",
            sender   = os.getenv("MAIL_USERNAME"),
            recipients = [admin_email],
            body     = f"""
A new SGBV report has been submitted anonymously.

Reference Code : {report.report_code}
Incident Type  : {report.incident_type}
District       : {report.district}
Location       : {report.location}
Victim Age     : {report.victim_age_range}
Victim Gender  : {report.victim_gender}
Relationship   : {report.relationship}
Urgent         : {"YES - IMMEDIATE ACTION REQUIRED" if report.urgent else "No"}
Submitted At   : {report.submitted_at.strftime("%Y-%m-%d %H:%M UTC")}

Description:
{report.description}

---
Please log in to the Nyaka AI Dashboard to review and take action.
This report is stored securely and the reporter's identity is protected.
            """,
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send SGBV admin email: {e}")


# ── Public: Submit Report ─────────────────────────────────────────────────────
@sgbv_bp.route("/report", methods=["GET", "POST"])
def report():
    """Anonymous SGBV report submission — NO login required."""
    if request.method == "POST":
        code = _generate_code()
        report = SGBVReport(
            report_code      = code,
            incident_type    = request.form.get("incident_type"),
            description      = request.form.get("description", "").strip(),
            location         = request.form.get("location", "").strip(),
            district         = request.form.get("district"),
            victim_age_range = request.form.get("victim_age_range"),
            victim_gender    = request.form.get("victim_gender"),
            relationship     = request.form.get("relationship"),
            urgent           = request.form.get("urgent") == "1",
            status           = "new",
        )
        db.session.add(report)
        db.session.commit()
        _notify_admin(report)
        return render_template(
            "sgbv_submitted.html",
            code=code,
            urgent=report.urgent
        )

    return render_template(
        "sgbv_report.html",
        incident_types = INCIDENT_TYPES,
        districts      = DISTRICTS,
        age_ranges     = AGE_RANGES,
        relationships  = RELATIONSHIPS,
    )


# ── Admin: View Reports ───────────────────────────────────────────────────────
@sgbv_bp.route("/admin")
@login_required
def admin():
    status_filter = request.args.get("status", "all")
    query = SGBVReport.query.order_by(SGBVReport.submitted_at.desc())
    if status_filter != "all":
        query = query.filter_by(status=status_filter)
    reports = query.all()
    counts = {
        "new":      SGBVReport.query.filter_by(status="new").count(),
        "reviewed": SGBVReport.query.filter_by(status="reviewed").count(),
        "resolved": SGBVReport.query.filter_by(status="resolved").count(),
    }
    return render_template("sgbv_admin.html", reports=reports, counts=counts, status_filter=status_filter)


@sgbv_bp.route("/admin/<int:report_id>/update", methods=["POST"])
@login_required
def update_report(report_id):
    report = SGBVReport.query.get_or_404(report_id)
    report.status      = request.form.get("status", report.status)
    report.notes       = request.form.get("notes", "").strip()
    report.reviewed_by = current_user.name
    db.session.commit()
    flash(f"Report {report.report_code} updated to '{report.status}'.", "success")
    return redirect(url_for("sgbv.admin"))
