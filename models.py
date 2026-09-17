from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    equipment_code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default="정상")
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
