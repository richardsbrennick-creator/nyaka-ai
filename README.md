# Nyaka AI Platform 🌍
**Nyaka Global Organization — Data-Driven Community Care System**

A free, open-source AI platform built for Nyaka Global Organization serving orphaned and vulnerable children and grandmothers in SW Uganda (Rukungiri & Kanungu districts).

---

## Features

| Module | Description |
|--------|-------------|
| 🎓 **Dropout Predictor** | ML model (Random Forest) predicts which students are at risk of dropping out based on attendance, grades, nutrition, distance, and family factors |
| 📊 **Dashboard** | Real-time overview of all students, risk levels, SGBV reports, and SMS activity. Login with Google (free) |
| 🛡️ **SGBV Anonymous Reporting** | Public form — no login needed. Reports go directly to admin + stored securely. Fully anonymous |
| 👵 **Grandmother SMS Advisory** | Send health, nutrition, attendance, and safety tips to grandmothers via Africa's Talking SMS API |

---

## Tech Stack (100% Free)

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ML | scikit-learn (Random Forest) |
| Auth | Google OAuth 2.0 (free) |
| SMS | Africa's Talking (free sandbox) |
| Frontend | Bootstrap 5 + Chart.js (CDN) |
| Hosting | Render.com or Railway.app (free tier) |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Set up Google OAuth (FREE)
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project → APIs & Services → Credentials
3. Create OAuth 2.0 Client ID (Web application)
4. Add authorized redirect URI: `http://localhost:5000/auth/callback`
5. Copy Client ID and Secret to `.env`

### 4. Set up Africa's Talking SMS (FREE sandbox)
1. Register at [africastalking.com](https://africastalking.com)
2. Use sandbox credentials for testing
3. Add API key to `.env`

### 5. Run the app
```bash
python app.py
```
Visit: http://localhost:5000

---

## Deploy Free on Render.com

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set environment variables from `.env`
5. Deploy — free tier available

---

## Project Structure

```
nyaka-ai/
├── app.py                  # Main Flask app
├── models.py               # Database models
├── requirements.txt
├── Procfile                # For Render/Railway deployment
├── routes/
│   ├── auth.py             # Google OAuth
│   ├── dashboard.py        # Main dashboard
│   ├── dropout.py          # Dropout predictor
│   ├── sgbv.py             # SGBV reporting
│   └── sms.py              # SMS advisory
├── utils/
│   ├── dropout_model.py    # ML model (Random Forest)
│   ├── sms_service.py      # Africa's Talking integration
│   └── seed.py             # Sample data for demo
└── templates/
    ├── base.html           # Shared layout
    ├── dashboard.html      # Main dashboard
    ├── dropout.html        # Student risk table
    ├── predict.html        # Predict single student
    ├── sgbv_report.html    # Public anonymous form
    ├── sgbv_admin.html     # Admin case management
    ├── sms.html            # SMS management
    └── login.html          # Google login page
```

---

## Data Context

Based on Nyaka Global Organization's real program:
- **~800+ students** across Nyaka Primary, Kutamba Primary, and Nyaka Secondary schools
- **20,000+ grandmothers** organized into self-governed groups across SW Uganda
- Districts: **Rukungiri** and **Kanungu**
- Focus: orphaned and vulnerable children (OVC) affected by HIV/AIDS

---

## For Board Presentation

The app seeds **36 sample students** and **8 grandmothers** automatically on first run, demonstrating all features with realistic Nyaka-context data.

---

*Built with ❤️ for Nyaka Global Organization*
