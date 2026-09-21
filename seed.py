from app import app, commit_or_rollback
from models import Equipment, db

# 딕셔너리 목록-> Equipment처럼 한 번에 객체로 풀어 넣기 쉬움
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
    # DB 작업은 Flask 앱 컨텍스트 안에서만 가능-> 임시 활성화
    with app.app_context():
        # models.py 설계도로 테이블이 없으면 생성
        db.create_all()
        # DB에 같은 장비번호가 이미 있으면 건너뛰고 없으면 새로 추가 대기시킨다.
        for kwargs in SAMPLE_EQUIPMENT:
            exists = Equipment.query.filter_by(equipment_code=kwargs["equipment_code"]).first()
            if not exists:
                db.session.add(Equipment(**kwargs))

        # 실제로 DB 파일에 씀 (예외 처리)
        if commit_or_rollback("테스트 데이터 등록 실패"):
            print(f"테스트 데이터 등록 완료 (총 {Equipment.query.count()}건)")


if __name__ == "__main__":
    seed()
