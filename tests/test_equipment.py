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
