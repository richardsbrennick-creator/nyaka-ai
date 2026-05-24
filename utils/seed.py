"""
Seed sample data for board presentation demo.
Based on Nyaka Global's real program context:
  - Districts: Rukungiri, Kanungu (SW Uganda)
  - ~800+ students across 2 primary + 1 secondary school
  - Grandmothers as primary caregivers
"""

import random
from datetime import datetime, timedelta

DISTRICTS   = ["Rukungiri", "Kanungu", "Kihihi", "Nyakagyezi"]
SCHOOLS     = ["Nyaka Primary School", "Kutamba Primary School", "Nyaka Secondary School"]
GRADES      = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "S1", "S2", "S3"]
GENDERS     = ["Female", "Male"]
GM_GROUPS   = [
    "Rukungiri Grandmothers Group A",
    "Kanungu Grandmothers Group B",
    "Kihihi Grandmothers Group C",
    "Nyakagyezi Grandmothers Group D",
]
STUDENT_NAMES = [
    "Aisha Nakato", "Brian Tumusiime", "Christine Akello", "David Mugisha",
    "Esther Namukasa", "Frank Byaruhanga", "Grace Atuhaire", "Henry Kato",
    "Irene Namutebi", "James Rwabuhinga", "Ketty Ampaire", "Lawrence Tukei",
    "Mary Kemigisha", "Nathan Asiimwe", "Olivia Nankunda", "Patrick Tumwine",
    "Queen Atuheire", "Robert Mwesigwa", "Sarah Kyomugisha", "Thomas Bwire",
    "Umar Ssekandi", "Violet Nabirye", "William Kabugo", "Xenia Atukunda",
    "Yvonne Nakimuli", "Zack Mugume", "Agnes Birungi", "Benard Twinamasiko",
    "Cynthia Kemunto", "Denis Ochieng", "Edith Nakabugo", "Felix Ssemwogerere",
    "Gloria Apio", "Hassan Waiswa", "Immaculate Nakato", "Joel Byamukama",
]
GM_NAMES = [
    "Mama Beatrice Kyomuhendo", "Mama Florence Tumusiime", "Mama Agnes Rwabuhinga",
    "Mama Josephine Atuhaire", "Mama Margret Kemigisha", "Mama Esther Byaruhanga",
    "Mama Rosemary Nankunda", "Mama Juliet Asiimwe",
]


def seed_sample_data():
    """Seed DB with sample Nyaka data if empty."""
    from extensions import db
    from models import Student, Grandmother

    if Student.query.count() > 0:
        return  # already seeded

    random.seed(42)

    # ── Grandmothers ──────────────────────────────────────────────────────────
    grandmothers = []
    for i, name in enumerate(GM_NAMES):
        gm = Grandmother(
            name         = name,
            phone        = f"+25670{random.randint(1000000, 9999999)}",
            district     = DISTRICTS[i % len(DISTRICTS)],
            group_name   = GM_GROUPS[i % len(GM_GROUPS)],
            num_children = random.randint(2, 10),
            language     = random.choice(["English", "Rukiga"]),
        )
        db.session.add(gm)
        grandmothers.append(gm)
    db.session.flush()

    # ── Students ──────────────────────────────────────────────────────────────
    for i, name in enumerate(STUDENT_NAMES):
        gm = grandmothers[i % len(grandmothers)]
        attendance = round(random.gauss(75, 20), 1)
        attendance = max(10.0, min(100.0, attendance))
        avg_score  = round(random.gauss(60, 20), 1)
        avg_score  = max(10.0, min(100.0, avg_score))
        meals      = random.choice([1.0, 1.5, 2.0, 2.0, 3.0])
        distance   = round(random.uniform(0.5, 12.0), 1)
        siblings   = random.randint(1, 8)
        prev_drop  = random.random() < 0.15

        # Simple risk heuristic for seeded data
        risk_score = 0.0
        if attendance < 60:   risk_score += 0.35
        if avg_score  < 50:   risk_score += 0.25
        if meals      < 2:    risk_score += 0.15
        if distance   > 8:    risk_score += 0.10
        if prev_drop:         risk_score += 0.15
        risk_score = min(1.0, risk_score + random.uniform(-0.05, 0.05))
        risk_score = max(0.0, risk_score)

        if risk_score >= 0.6:   label = "High"
        elif risk_score >= 0.3: label = "Medium"
        else:                   label = "Low"

        s = Student(
            name             = name,
            age              = random.randint(8, 18),
            gender           = GENDERS[i % 2],
            grade            = GRADES[i % len(GRADES)],
            district         = gm.district,
            school           = SCHOOLS[i % len(SCHOOLS)],
            attendance_pct   = attendance,
            avg_grade_score  = avg_score,
            meals_per_day    = meals,
            distance_km      = distance,
            has_both_parents = False,
            caregiver_is_gm  = True,
            num_siblings     = siblings,
            prev_dropout     = prev_drop,
            dropout_risk     = round(risk_score, 3),
            risk_label       = label,
            grandmother_phone= gm.phone,
            created_at       = datetime.utcnow() - timedelta(days=random.randint(0, 180)),
        )
        db.session.add(s)

    db.session.commit()
    print("[Nyaka] ✅ Sample data seeded successfully.")
