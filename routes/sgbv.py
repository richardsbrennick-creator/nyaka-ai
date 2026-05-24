import random
import string
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from models import SGBVReport
from extensions import db, mail

sgbv_bp = Blueprint("sgbv", __name__, url_prefix="/sgbv")

INCIDENT_TYPES = [
    "Sexual Violence", "Physical Violence", "Emotional / Psychological Abuse",
    "Child Marriage", "Female Genital Mutilation (FGM)", "Neglect / Abandonment",
    "Economic Abuse", "Other",
]
DISTRICTS     = ["Rukungiri", "Kanungu", "Kihihi", "Nyakagyezi", "Other"]
AGE_RANGES    = ["Under 10", "10-14", "15-17", "18-24", "25-34", "35+", "Unknown"]
RELATIONSHIPS = [
    "Parent / Guardian", "Relative", "Teacher", "Neighbor",
    "Stranger", "Partner / Spouse", "Unknown", "Other"
]


def _generate_code():
    return "NYK-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def _notify_admin(report):
    admin_email = os.getenv("ADMIN_EMAIL", "richardsbrennick@gmail.com")
    try:
        msg = Message(
            subject    = f"[NYAKA SGBV] New Report {report.report_code}",
            sender     = os.getenv("MAIL_USERNAME", admin_email),
            recipients = [admin_email],
            body       = (
                f"Reference: {report.report_code}\n"
                f"Type: {report.incident_type}\n"
                f"District: {report.district}\n"
                f"Urgent: {'YES' if report.urgent else 'No'}\n\n"
                f"{report.description}"
            ),
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"SGBV email failed: {e}")


@sgbv_bp.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        code = _generate_code()
        r = SGBVReport(
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
        db.session.add(r)
        db.session.commit()
        _notify_admin(r)
        return render_template("sgbv_submitted.html", code=code, urgent=r.urgent)

    return render_template(
        "sgbv_report.html",
        incident_types=INCIDENT_TYPES, districts=DISTRICTS,
        age_ranges=AGE_RANGES, relationships=RELATIONSHIPS,
    )


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
    r = SGBVReport.query.get_or_404(report_id)
    r.status      = request.form.get("status", r.status)
    r.notes       = request.form.get("notes", "").strip()
    r.reviewed_by = current_user.name
    db.session.commit()
    flash(f"Report {r.report_code} updated.", "success")
    return redirect(url_for("sgbv.admin"))
