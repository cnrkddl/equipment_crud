---
name: tdd
description: equipment_crud(Flask + pytest)에서 CRUD 기능(목록/상세/등록/수정/삭제, 입력값 검증)을 하나씩 구현할 때 사용하는 red-green TDD 루프. 새 라우트를 추가하거나, 검증 로직을 넣거나, 버그를 고칠 때 트리거.
---

# TDD in equipment_crud (Flask + pytest)

빨강(실패하는 테스트) → 초록(최소 구현) 루프. 내부 구현이 아니라 **공개 경계(퍼블릭 인터페이스)**를 통해 동작을 검증한다.

## 이 프로젝트의 seam(경계)

테스트는 아래 경계에서만 검증한다. 이 경계 밖(예: `db.session` 호출 여부, SQLAlchemy 쿼리 내부)은 절대 모킹하거나 직접 assert하지 않는다.

- Flask 라우트 (`app.test_client()`로 보내는 실제 HTTP 요청)
  - `GET/POST /equipment`, `/equipment/create`, `/equipment/<id>`, `/equipment/<id>/edit`, `/equipment/<id>/delete`
- DB 상태는 **다시 조회해서** 확인한다 (`Equipment.query.get(...)` 등), mock으로 대체하지 않는다.

## 루프 규칙

1. 과제 지시서(5. 필수 구현 기능 / 9. 입력값 검증) 중 항목 하나를 고른다.
2. `tests/test_equipment.py`에 실패하는 테스트 하나를 먼저 쓴다. 반드시 HTTP 응답(status code, redirect 위치, 렌더된 내용)이나 후속 GET으로 관찰 가능한 결과로 검증한다.
3. `pytest`를 실행해 "예상한 이유로" 실패하는지 확인한다.
4. `app.py` / `models.py`에 테스트를 통과시키는 최소한의 코드만 작성한다.
5. `pytest`를 다시 실행해 초록을 확인한다.
6. 리팩터링은 초록 상태에서만, 별도 리뷰 단계에서 한다 (`/code-review` 참고). red-green 루프 중간에 구조를 바꾸지 않는다.
7. 한 사이클 = 한 seam, 한 테스트, 한 최소 구현. 여러 테스트를 한 번에 몰아서 먼저 쓰지 않는다(수평 슬라이싱 금지).

## 좋은 테스트 / 나쁜 테스트

```python
# GOOD: 공개 인터페이스(HTTP)로 관찰 가능한 동작을 검증
def test_duplicate_equipment_code_is_rejected(client):
    client.post("/equipment/create", data={"equipment_code": "EQ-001", "name": "카메라"})
    response = client.post(
        "/equipment/create", data={"equipment_code": "EQ-001", "name": "다른 장비"}
    )
    assert "이미 등록된 장비번호입니다".encode() in response.data

# BAD: 내부 구현(SQLAlchemy 세션)을 직접 모킹
def test_create_calls_db_add(client, mocker):
    mock_add = mocker.patch("models.db.session.add")
    client.post("/equipment/create", data={"equipment_code": "EQ-001", "name": "카메라"})
    mock_add.assert_called_once()  # 리팩터링하면 바로 깨짐 -> 지양
```

- 기대값은 코드와 같은 로직으로 재계산하지 말고 독립적인 리터럴로 쓴다 (tautological test 금지).
- 테스트 이름은 지시서/도메인 용어(장비번호, 장비상태 등)를 그대로 쓴다.

## 테스트 DB

`conftest.py`의 `app`/`client` fixture는 매 테스트마다 새 SQLite(파일 또는 in-memory)로 `db.create_all()` 후 테스트가 끝나면 `db.drop_all()`로 정리한다. 실제 `instance/equipment.db`는 절대 건드리지 않는다.

## 모킹 기준

- 외부 시스템 경계(이 프로젝트엔 현재 없음: 외부 API, 이메일 등)만 모킹 대상.
- `db.session`, `Equipment` 모델, 이 프로젝트가 통제하는 코드는 모킹하지 않는다 — 테스트 DB로 실제로 왕복시킨다.
