from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from models import Student
from utils.dropout_model import predict_dropout
from utils.sms_service import send_dropout_alert
from app import db

dropout_bp = Blueprint("dropout", __name__, url_prefix="/dropout")


@dropout_bp.route("/")
@login_required
def index():
    students = Student.query.order_by(Student.dropout_risk.desc()).all()
    return render_template("dropout.html", students=students)


@dropout_bp.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    result = None
    if request.method == "POST":
        data = {
            "attendance_pct":  float(request.form.get("attendance_pct", 75)),
            "avg_grade_score": float(request.form.get("avg_grade_score", 60)),
            "meals_per_day":   float(request.form.get("meals_per_day", 2)),
            "distance_km":     float(request.form.get("distance_km", 2)),
            "has_both_parents":request.form.get("has_both_parents") == "1",
            "caregiver_is_gm": request.form.get("caregiver_is_gm") == "1",
            "num_siblings":    int(request.form.get("num_siblings", 3)),
            "prev_dropout":    request.form.get("prev_dropout") == "1",
        }
        result = predict_dropout(data)
        student_name = request.form.get("student_name", "").strip()
        if student_name:
            s = Student(
                name=student_name,
                grade=request.form.get("grade", ""),
                school=request.form.get("school", ""),
                district=request.form.get("district", ""),
                attendance_pct=data["attendance_pct"],
                avg_grade_score=data["avg_grade_score"],
                meals_per_day=data["meals_per_day"],
                distance_km=data["distance_km"],
                has_both_parents=data["has_both_parents"],
                caregiver_is_gm=data["caregiver_is_gm"],
                num_siblings=data["num_siblings"],
                prev_dropout=data["prev_dropout"],
                dropout_risk=result["probability"],
                risk_label=result["label"],
                grandmother_phone=request.form.get("grandmother_phone", ""),
            )
            db.session.add(s)
            db.session.commit()
            flash(f"Student '{student_name}' saved with {result['label']} risk.", "info")
    return render_template("predict.html", result=result)


@dropout_bp.route("/run-all", methods=["POST"])
@login_required
def run_all():
    students = Student.query.all()
    for s in students:
        data = {
            "attendance_pct": s.attendance_pct, "avg_grade_score": s.avg_grade_score,
            "meals_per_day": s.meals_per_day, "distance_km": s.distance_km,
            "has_both_parents": s.has_both_parents, "caregiver_is_gm": s.caregiver_is_gm,
            "num_siblings": s.num_siblings, "prev_dropout": s.prev_dropout,
        }
        result = predict_dropout(data)
        s.dropout_risk = result["probability"]
        s.risk_label   = result["label"]
    db.session.commit()
    flash(f"Updated predictions for {len(students)} students.", "success")
    return redirect(url_for("dropout.index"))


@dropout_bp.route("/alert/<int:student_id>", methods=["POST"])
@login_required
def send_alert(student_id):
    student = Student.query.get_or_404(student_id)
    if not student.grandmother_phone:
        flash("No grandmother phone number on file.", "warning")
        return redirect(url_for("dropout.index"))
    result = send_dropout_alert(student.grandmother_phone, student.name)
    if result.get("success"):
        flash(f"SMS alert sent to grandmother of {student.name}.", "success")
    else:
        flash(f"SMS failed: {result.get('error', 'Unknown error')}", "danger")
    return redirect(url_for("dropout.index"))


@dropout_bp.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    return jsonify(predict_dropout(data))
