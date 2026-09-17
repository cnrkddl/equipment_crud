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


def test_필수값을_모두_입력하면_장비_등록_후_목록_화면으로_이동하고_목록에_표시된다(client):
    response = client.post(
        "/equipment/create",
        data={
            "equipment_code": "EQ-100",
            "name": "열화상 카메라",
            "location": "",
            "status": "정상",
            "description": "",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/equipment"

    list_response = client.get("/equipment")

    assert "EQ-100".encode() in list_response.data
    assert "열화상 카메라".encode() in list_response.data


def test_장비번호를_비워두면_등록이_거부되고_안내_메시지가_표시된다(client):
    response = client.post(
        "/equipment/create",
        data={
            "equipment_code": "",
            "name": "드론 카메라",
            "location": "",
            "status": "정상",
            "description": "",
        },
    )

    assert response.status_code == 200
    assert "장비번호는 필수입니다".encode() in response.data

    list_response = client.get("/equipment")

    assert "드론 카메라".encode() not in list_response.data


def test_장비명을_비워두면_등록이_거부되고_안내_메시지가_표시된다(client):
    response = client.post(
        "/equipment/create",
        data={
            "equipment_code": "EQ-101",
            "name": "",
            "location": "",
            "status": "정상",
            "description": "",
        },
    )

    assert response.status_code == 200
    assert "장비명은 필수입니다".encode() in response.data

    list_response = client.get("/equipment")

    assert "EQ-101".encode() not in list_response.data


def test_이미_등록된_장비번호로_등록하면_거부되고_기존_장비명이_유지된다(client, db):
    equipment = Equipment(
        equipment_code="EQ-200",
        name="기존 장비",
        location="",
        status="정상",
        registered_at=datetime(2024, 5, 1),
    )
    db.session.add(equipment)
    db.session.commit()

    response = client.post(
        "/equipment/create",
        data={
            "equipment_code": "EQ-200",
            "name": "신규 장비",
            "location": "",
            "status": "정상",
            "description": "",
        },
    )

    assert response.status_code == 200
    assert "이미 등록된 장비번호입니다".encode() in response.data

    detail_response = client.get(f"/equipment/{equipment.id}")

    assert "기존 장비".encode() in detail_response.data
    assert "신규 장비".encode() not in detail_response.data


def test_등록이_완료되면_목록_화면에_등록_완료_안내_메시지가_표시된다(client):
    response = client.post(
        "/equipment/create",
        data={
            "equipment_code": "EQ-300",
            "name": "레이저 스캐너",
            "location": "",
            "status": "정상",
            "description": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "등록이 완료되었습니다".encode() in response.data


def test_등록시_입력값_앞뒤_공백이_제거되어_저장된다(client, db):
    client.post(
        "/equipment/create",
        data={
            "equipment_code": "  EQ-400  ",
            "name": "  스캐너  ",
            "location": "  테스트실  ",
            "status": "정상",
            "description": "  설명입니다  ",
        },
    )

    equipment = Equipment.query.filter_by(equipment_code="EQ-400").first()

    assert equipment is not None
    assert equipment.location == "테스트실"
    assert equipment.description == "설명입니다"
