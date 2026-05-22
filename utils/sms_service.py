"""
Grandmother SMS Advisory Service
==================================
Uses Africa's Talking API to send SMS advisories to grandmothers.
Topics: child health, nutrition, school attendance, SGBV awareness.
"""

import os
import africastalking
from datetime import datetime

# Initialize Africa's Talking
AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY  = os.getenv("AT_API_KEY", "")
AT_SENDER   = os.getenv("AT_SENDER_ID", "NYAKA")

# Advisory message templates (English + Rukiga)
ADVISORIES = {
    "attendance": {
        "English": (
            "NYAKA ADVISORY: Dear Grandmother, please ensure your child attends school "
            "every day. Regular attendance is key to their future. "
            "Call Nyaka: 0800-NYAKA for support."
        ),
        "Rukiga": (
            "NYAKA: Maama, kora neza omwana wawe agenda omusomero buri eizooba. "
            "Okusoma ni omugisha gw'ejo hazaaza. Tuurika: 0800-NYAKA."
        ),
    },
    "nutrition": {
        "English": (
            "NYAKA ADVISORY: A well-fed child learns better. Try to provide at least "
            "2 meals a day including vegetables. Nyaka nutrition support is available. "
            "Call: 0800-NYAKA."
        ),
        "Rukiga": (
            "NYAKA: Omwana orikuriirwa neza asiima neza. Mpa omwana oburiijo "
            "obw'emitooma. Tubaasa kukumaraho. Tuurika: 0800-NYAKA."
        ),
    },
    "health": {
        "English": (
            "NYAKA HEALTH TIP: Take your child for a health check-up this month. "
            "Nyaka clinic offers free services. Stay healthy, stay in school. "
            "Call: 0800-NYAKA."
        ),
        "Rukiga": (
            "NYAKA AMAGARA: Twara omwana wawe omu kirinika ky'amagara ono mwezi. "
            "Kirinika ya Nyaka niyo mahoro. Tuurika: 0800-NYAKA."
        ),
    },
    "sgbv_awareness": {
        "English": (
            "NYAKA SAFETY: Protect your children. If you see or experience violence, "
            "report anonymously at nyakaglobal.org/report or call 0800-NYAKA. "
            "You are not alone."
        ),
        "Rukiga": (
            "NYAKA MUTEKANO: Linda abaana bawe. Nk'obona obusha, bwatangaza "
            "omu nyakaglobal.org/report oba tuurika 0800-NYAKA. Tutakurega."
        ),
    },
    "dropout_alert": {
        "English": (
            "NYAKA ALERT: We are concerned about {name}'s school attendance. "
            "Please encourage them to attend school. A Nyaka counselor will visit soon. "
            "Call: 0800-NYAKA."
        ),
        "Rukiga": (
            "NYAKA KUMENYESHA: Turakangabira okusoma kwa {name}. "
            "Mwigisha agenda omusomero. Omushomesa wa Nyaka azaza. Tuurika: 0800-NYAKA."
        ),
    },
}


def _init_at():
    """Initialize Africa's Talking SDK."""
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    return africastalking.SMS


def send_sms(phone: str, message: str, category: str = "advisory") -> dict:
    """
    Send a single SMS via Africa's Talking.

    Returns dict with status and messageId.
    """
    from app import db
    from models import SMSLog

    log = SMSLog(recipient=phone, message=message, category=category)
    db.session.add(log)

    try:
        sms = _init_at()
        response = sms.send(message, [phone], sender_id=AT_SENDER)
        recipients = response.get("SMSMessageData", {}).get("Recipients", [])
        if recipients:
            status = recipients[0].get("status", "unknown")
            log.status = status
        else:
            log.status = "sent"
        db.session.commit()
        return {"success": True, "response": response}
    except Exception as e:
        log.status = f"error: {str(e)[:100]}"
        db.session.commit()
        return {"success": False, "error": str(e)}


def send_advisory(grandmother, topic: str = "attendance") -> dict:
    """Send a topic-based advisory to a grandmother."""
    lang     = grandmother.language if grandmother.language in ("English", "Rukiga") else "English"
    template = ADVISORIES.get(topic, ADVISORIES["attendance"])
    message  = template.get(lang, template["English"])
    return send_sms(grandmother.phone, message, category=f"advisory_{topic}")


def send_dropout_alert(grandmother_phone: str, student_name: str, language: str = "English") -> dict:
    """Send a dropout risk alert to a grandmother."""
    lang     = language if language in ("English", "Rukiga") else "English"
    template = ADVISORIES["dropout_alert"][lang].format(name=student_name.split()[0])
    return send_sms(grandmother_phone, template, category="dropout_alert")


def broadcast_advisory(topic: str = "attendance") -> dict:
    """Send advisory to ALL grandmothers in the database."""
    from models import Grandmother
    grandmothers = Grandmother.query.all()
    results = {"sent": 0, "failed": 0, "total": len(grandmothers)}
    for gm in grandmothers:
        result = send_advisory(gm, topic)
        if result.get("success"):
            results["sent"] += 1
        else:
            results["failed"] += 1
    return results
