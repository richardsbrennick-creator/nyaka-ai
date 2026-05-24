from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from models import Grandmother, SMSLog
from utils.sms_service import send_advisory, broadcast_advisory, send_sms
from app import db

sms_bp = Blueprint("sms", __name__, url_prefix="/sms")

TOPICS = {
    "attendance":     "School Attendance Reminder",
    "nutrition":      "Nutrition & Meals Advisory",
    "health":         "Health Check-up Reminder",
    "sgbv_awareness": "SGBV Safety Awareness",
}


@sms_bp.route("/")
@login_required
def index():
    grandmothers = Grandmother.query.order_by(Grandmother.district).all()
    recent_logs  = SMSLog.query.order_by(SMSLog.sent_at.desc()).limit(20).all()
    return render_template("sms.html", grandmothers=grandmothers, recent_logs=recent_logs, topics=TOPICS)


@sms_bp.route("/send-individual", methods=["POST"])
@login_required
def send_individual():
    gm = Grandmother.query.get_or_404(request.form.get("grandmother_id"))
    result = send_advisory(gm, request.form.get("topic", "attendance"))
    if result.get("success"):
        flash(f"SMS sent to {gm.name}.", "success")
    else:
        flash(f"SMS failed: {result.get('error', 'Unknown')}", "danger")
    return redirect(url_for("sms.index"))


@sms_bp.route("/broadcast", methods=["POST"])
@login_required
def broadcast():
    result = broadcast_advisory(request.form.get("topic", "attendance"))
    flash(f"Broadcast: {result['sent']} sent, {result['failed']} failed of {result['total']}.",
          "success" if result["failed"] == 0 else "warning")
    return redirect(url_for("sms.index"))


@sms_bp.route("/custom", methods=["POST"])
@login_required
def custom_sms():
    phone   = request.form.get("phone", "").strip()
    message = request.form.get("message", "").strip()
    if not phone or not message:
        flash("Phone and message required.", "warning")
        return redirect(url_for("sms.index"))
    result = send_sms(phone, message, category="custom")
    flash(f"SMS sent to {phone}." if result.get("success") else f"Failed: {result.get('error')}", 
          "success" if result.get("success") else "danger")
    return redirect(url_for("sms.index"))


@sms_bp.route("/logs")
@login_required
def logs():
    logs = SMSLog.query.order_by(SMSLog.sent_at.desc()).limit(100).all()
    return render_template("sms_logs.html", logs=logs)
