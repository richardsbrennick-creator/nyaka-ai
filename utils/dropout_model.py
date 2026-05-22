"""
Student Dropout Predictor
==========================
Uses a Random Forest classifier trained on Nyaka-style sample data.
Features mirror real risk factors for orphaned/vulnerable children in SW Uganda.
"""

import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), "dropout_model.pkl")

# Feature names (order matters)
FEATURES = [
    "attendance_pct",    # % school days attended
    "avg_grade_score",   # average test score 0-100
    "meals_per_day",     # nutrition indicator
    "distance_km",       # distance to school
    "has_both_parents",  # 0/1
    "caregiver_is_gm",   # 0/1 grandmother caregiver
    "num_siblings",      # number of siblings
    "prev_dropout",      # 0/1 previously dropped out
]


def _generate_training_data(n=500):
    """
    Generate synthetic but realistic training data based on
    Nyaka's program context (SW Uganda, orphaned/vulnerable children).
    """
    np.random.seed(42)
    X, y = [], []

    for _ in range(n):
        attendance  = np.clip(np.random.normal(72, 22), 5, 100)
        score       = np.clip(np.random.normal(58, 22), 5, 100)
        meals       = np.random.choice([1, 1.5, 2, 2, 3], p=[0.15, 0.20, 0.35, 0.20, 0.10])
        distance    = np.clip(np.random.exponential(4), 0.3, 15)
        both_parents= int(np.random.random() < 0.08)   # most are orphans
        gm_carer    = int(np.random.random() < 0.75)
        siblings    = np.random.randint(1, 10)
        prev_drop   = int(np.random.random() < 0.12)

        # Dropout probability based on risk factors
        risk = 0.0
        if attendance < 50:  risk += 0.40
        elif attendance < 70: risk += 0.20
        if score < 40:       risk += 0.30
        elif score < 55:     risk += 0.15
        if meals < 2:        risk += 0.15
        if distance > 8:     risk += 0.12
        if prev_drop:        risk += 0.20
        if not gm_carer and not both_parents: risk += 0.10
        risk = np.clip(risk + np.random.normal(0, 0.08), 0, 1)

        label = 1 if risk > 0.45 else 0
        X.append([attendance, score, meals, distance, both_parents, gm_carer, siblings, prev_drop])
        y.append(label)

    return np.array(X), np.array(y)


def train_and_save_model():
    """Train the model and save to disk."""
    X, y = _generate_training_data(600)
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42,
            class_weight="balanced"
        ))
    ])
    model.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print("[Nyaka] ✅ Dropout model trained and saved.")
    return model


def load_model():
    """Load model from disk, training if not found."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return train_and_save_model()


def predict_dropout(student_data: dict) -> dict:
    """
    Predict dropout risk for a single student.

    Args:
        student_data: dict with keys matching FEATURES

    Returns:
        dict with 'probability' (0-1), 'label' (Low/Medium/High),
        'risk_factors' list
    """
    model = load_model()

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

    X = np.array([features])
    prob = float(model.predict_proba(X)[0][1])

    if prob >= 0.65:
        label = "High"
        color = "danger"
    elif prob >= 0.35:
        label = "Medium"
        color = "warning"
    else:
        label = "Low"
        color = "success"

    # Identify top risk factors
    risk_factors = []
    if features[0] < 60:
        risk_factors.append(f"Low attendance ({features[0]:.0f}%)")
    if features[1] < 50:
        risk_factors.append(f"Low academic scores ({features[1]:.0f}/100)")
    if features[2] < 2:
        risk_factors.append("Insufficient nutrition (< 2 meals/day)")
    if features[3] > 8:
        risk_factors.append(f"Long distance to school ({features[3]:.1f} km)")
    if features[7]:
        risk_factors.append("Previous dropout history")
    if not risk_factors:
        risk_factors.append("No major risk factors identified")

    return {
        "probability": round(prob, 3),
        "percentage":  round(prob * 100, 1),
        "label":       label,
        "color":       color,
        "risk_factors": risk_factors,
    }


def batch_predict(students: list) -> list:
    """Run predictions on a list of student dicts."""
    return [predict_dropout(s) for s in students]


# Train model on first import if not cached
if not os.path.exists(MODEL_PATH):
    train_and_save_model()
