# SQL 대신 파이썬 문법으로 테이블 설계도 작성한 파일 
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 등록/수정 폼의 선택지와 목록/상세 화면의 상태 뱃지 색상이 이 목록 하나를 같이 참조한다.
EQUIPMENT_STATUSES = ["정상", "점검중", "고장"]
STATUS_STYLE_MAP = {"정상": "ok", "점검중": "pending", "고장": "fault"}


def status_style(status):
    return STATUS_STYLE_MAP.get(status, "pending")


# db.Model을 상속하면 SQLAlchemy가 이 클래스를 테이블 하나로 인식
class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    # 장비 고유 코드
    equipment_code = db.Column(db.String(30), unique=True, nullable=False)
    # 장비 이름
    name = db.Column(db.String(100), nullable=False)
    # 장비 위치
    location = db.Column(db.String(100))
    # 장비 상태
    status = db.Column(db.String(20), default="정상")
    # 등록 시간
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 비고
    description = db.Column(db.Text)
