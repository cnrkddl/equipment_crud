from datetime import datetime

from models import Equipment


def test_장비_목록_조회시_등록된_장비가_표시된다(client, db):
    equipment = Equipment(
        equipment_code="EQ-001",
        name="RGB 카메라",
        location="테스트실",
        status="정상",
        registered_at=datetime(2024, 1, 1),
    )
    db.session.add(equipment)
    db.session.commit()

    response = client.get("/equipment")

    assert response.status_code == 200
    assert "EQ-001".encode() in response.data
    assert "RGB 카메라".encode() in response.data
    assert "테스트실".encode() in response.data
    assert "정상".encode() in response.data


def test_등록된_장비가_없으면_안내_메시지가_표시된다(client):
    response = client.get("/equipment")

    assert response.status_code == 200
    assert "등록된 장비가 없습니다".encode() in response.data


def test_장비_상세_조회시_전체_등록_정보가_표시된다(client, db):
    equipment = Equipment(
        equipment_code="EQ-002",
        name="적외선 센서",
        location="선별실",
        status="점검중",
        registered_at=datetime(2024, 3, 15),
        description="분해능 조정 필요",
    )
    db.session.add(equipment)
    db.session.commit()

    response = client.get(f"/equipment/{equipment.id}")

    assert response.status_code == 200
    assert "EQ-002".encode() in response.data
    assert "적외선 센서".encode() in response.data
    assert "선별실".encode() in response.data
    assert "점검중".encode() in response.data
    assert "2024-03-15".encode() in response.data
    assert "분해능 조정 필요".encode() in response.data


def test_존재하지_않는_id로_상세_조회시_오류_처리된다(client):
    response = client.get("/equipment/9999")

    assert response.status_code == 404
    assert "해당 장비를 찾을 수 없습니다".encode() in response.data
