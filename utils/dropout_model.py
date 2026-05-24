"""
Student Dropout Predictor — lazy-loaded Random Forest model.
Model trains on first prediction request, not at import/startup.
"""

import numpy as np
import pickle
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "dropout_model.pkl")

# Cached model instance
_model = None


def _generate_training_data(n=300):
    """Synthetic but realistic training data for SW Uganda orphaned children."""
    np.random.seed(42)
    X, y = [], []
    for _ in range(n):
        attendance   = np.clip(np.random.normal(72, 22), 5, 100)
        score        = np.clip(np.random.normal(58, 22), 5, 100)
        meals        = np.random.choice([1, 1.5, 2, 2, 3], p=[0.15, 0.20, 0.35, 0.20, 0.10])
        distance     = np.clip(np.random.exponential(4), 0.3, 15)
        both_parents = int(np.random.random() < 0.08)
        gm_carer     = int(np.random.random() < 0.75)
        siblings     = np.random.randint(1, 10)
        prev_drop    = int(np.random.random() < 0.12)

        risk = 0.0
        if attendance < 50:  risk += 0.40
        elif attendance < 70: risk += 0.20
        if score < 40:       risk += 0.30
        elif score < 55:     risk += 0.15
        if meals < 2:        risk += 0.15
        if distance > 8:     risk += 0.12
        if prev_drop:        risk += 0.20
        risk = np.clip(risk + np.random.normal(0, 0.08), 0, 1)

        X.append([attendance, score, meals, distance, both_parents, gm_carer, siblings, prev_drop])
        y.append(1 if risk > 0.45 else 0)
    return np.array(X), np.array(y)


def _train_model():
    """Train and return the model (does NOT save to disk on read-only filesystems)."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    X, y = _generate_training_data(300)
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42, class_weight="balanced"))
    ])
    model.fit(X, y)
    return model


def _get_model():
    """Return cached model, training if needed."""
    global _model
    if _model is None:
        # Try loading from disk first
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    _model = pickle.load(f)
                return _model
            except Exception:
                pass
        # Train fresh
        _model = _train_model()
        # Try saving (may fail on read-only FS — that's fine)
        try:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(_model, f)
        except Exception:
            pass
    return _model


def predict_dropout(student_data: dict) -> dict:
    """Predict dropout risk for a single student."""
    model = _get_model()

    features = [
        float(student_data.get("attendance_pct", 75)),
        float(student_data.get("avg_grade_score", 60)),
        float(student_data.get("meals_per_day", 2)),
        float(student_data.get("distance_km", 2)),
        int(bool(student_data.get("has_both_parents", False))),
        int(bool(student_data.get("caregiver_is_gm", True))),
        int(student_data.get("num_siblings", 3)),
        int(bool(student_data.get("prev_dropout", False))),
    ]

    X    = np.array([features])
    prob = float(model.predict_proba(X)[0][1])

    if prob >= 0.65:
        label, color = "High", "danger"
    elif prob >= 0.35:
        label, color = "Medium", "warning"
    else:
        label, color = "Low", "success"

    risk_factors = []
    if features[0] < 60:  risk_factors.append(f"Low attendance ({features[0]:.0f}%)")
    if features[1] < 50:  risk_factors.append(f"Low academic scores ({features[1]:.0f}/100)")
    if features[2] < 2:   risk_factors.append("Insufficient nutrition (< 2 meals/day)")
    if features[3] > 8:   risk_factors.append(f"Long distance to school ({features[3]:.1f} km)")
    if features[7]:       risk_factors.append("Previous dropout history")
    if not risk_factors:  risk_factors.append("No major risk factors identified")

    return {
        "probability":  round(prob, 3),
        "percentage":   round(prob * 100, 1),
        "label":        label,
        "color":        color,
        "risk_factors": risk_factors,
    }
