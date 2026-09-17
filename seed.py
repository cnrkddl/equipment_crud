from app import app
from models import Equipment, db

SAMPLE_EQUIPMENT = [
    {
        "equipment_code": "EQ-001",
        "name": "RGB 카메라",
        "location": "테스트실",
        "status": "정상",
        "description": "폐플라스틱 선별용 비전 카메라",
    },
    {
        "equipment_code": "EQ-002",
        "name": "근적외선(NIR) 센서",
        "location": "선별라인 1",
        "status": "점검중",
        "description": "재질 판별용 NIR 센서",
    },
    {
        "equipment_code": "EQ-003",
        "name": "에어젯 분사장치",
        "location": "선별라인 2",
        "status": "고장",
        "description": "선별된 플라스틱 분리용 공압 장치",
    },
]


def seed():
    with app.app_context():
        db.create_all()
        for data in SAMPLE_EQUIPMENT:
            exists = Equipment.query.filter_by(equipment_code=data["equipment_code"]).first()
            if not exists:
                db.session.add(Equipment(**data))
        db.session.commit()
        print(f"테스트 데이터 등록 완료 (총 {Equipment.query.count()}건)")


if __name__ == "__main__":
    seed()
