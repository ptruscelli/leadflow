from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Lead

def populate_db(count: int = 5):
    now = datetime.now(timezone.utc)
    templates = [
        {
            "name": "Amira Hassan",
            "email": "amira.hassan@northline.example",
            "company": "Northline Media",
            "phone": "07700 900123",
            "source": "google",
            "message": "We're rebranding this autumn and would like a quote for a new site and brand guidelines.",
            "status": "new",
            "created_offset": timedelta(hours=3),
            "updated_offset": timedelta(hours=3),
        },
        {
            "name": "James Okonkwo",
            "email": "james@harborandco.example",
            "company": "Harbor & Co",
            "phone": None,
            "source": "referral",
            "message": "Referred by a former client. Looking for social assets for a product launch next month.",
            "status": "new",
            "created_offset": timedelta(days=1),
            "updated_offset": timedelta(days=1),
        },
        {
            "name": "Priya Shah",
            "email": "priya.shah@willowretail.example",
            "company": "Willow Retail",
            "phone": "020 7946 0958",
            "source": "social_media",
            "message": "Saw your work on Instagram. Can you take on packaging design for a small spring range?",
            "status": "contacted",
            "note": "Emailed intro and booked a call for Thursday.",
            "created_offset": timedelta(days=4),
            "updated_offset": timedelta(days=2),
        },
        {
            "name": "Tom Ellis",
            "email": "tom.ellis@brightpath.example",
            "company": "Brightpath Labs",
            "phone": "0161 496 0123",
            "source": "other",
            "message": "Need a pitch deck and landing page for a seed round. Timeline is tight — about three weeks.",
            "status": "qualified",
            "note": "Budget confirmed. Waiting on brand assets before sending a proposal.",
            "created_offset": timedelta(days=8),
            "updated_offset": timedelta(days=1),
        },
        {
            "name": "Sofia Ricci",
            "email": "sofia@atelierluce.example",
            "company": "Atelier Luce",
            "phone": None,
            "source": "google",
            "message": "Interested in a one-page site for our studio. Decided to pause until next financial year.",
            "status": "closed",
            "note": "Not proceeding this quarter. Check back in January.",
            "created_offset": timedelta(days=14),
            "updated_offset": timedelta(days=5),
        },
    ]

    db = SessionLocal()
    try:
        if db.scalar(select(func.count()).select_from(Lead)): # only generate leads if the database is empty
            return

        leads = []
        for i in range(count):
            template = templates[i % len(templates)]
            batch = i // len(templates) + 1
            local, domain = template["email"].split("@", 1)
            leads.append(
                Lead(
                    name=template["name"] if batch == 1 else f"{template['name']} ({batch})",
                    email=f"{local}+{i}@{domain}",
                    company=template["company"],
                    phone=template["phone"],
                    source=template["source"],
                    message=template["message"],
                    status=template["status"],
                    note=template.get("note"),
                    created_at=now - template["created_offset"] - timedelta(minutes=i),
                    updated_at=now - template["updated_offset"] - timedelta(minutes=i),
                )
            )

        db.add_all(leads)
        db.commit()
    finally:
        db.close()
