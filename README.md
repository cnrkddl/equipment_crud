# 장비관리 CRUD 시스템

Flask + SQLite 기반의 장비 정보 관리 웹 애플리케이션입니다.

## 개발 환경

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- SQLite
- Bootstrap 5

## 실행 방법

```bash
# 가상환경 활성화
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

실행 후 브라우저에서 http://127.0.0.1:5000 접속.

## 테스트 데이터 등록

초기 테스트 장비 3건(정상/점검중/고장 각 1건)을 등록합니다. 이미 등록된
장비번호는 건너뜁니다.

```bash
python seed.py
```

## 테스트

```bash
pip install -r requirements-dev.txt
pytest
```

목록/상세/등록/수정/삭제 및 입력값 검증, 오류 처리를 포함해 24개의
테스트 케이스로 확인합니다.

## 폴더 구조

```
equipment_crud/
├── app.py
├── models.py
├── seed.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── instance/
│   └── equipment.db
├── templates/
│   ├── base.html
│   ├── equipment_list.html
│   ├── equipment_detail.html
│   ├── equipment_create.html
│   └── equipment_edit.html
├── static/
│   └── style.css
└── tests/
    ├── conftest.py
    └── test_equipment.py
```

## 기능

- 장비 등록 (Create)
- 장비 목록 조회 (Read)
- 장비 상세 조회 (Read)
- 장비 정보 수정 (Update)
- 장비 삭제 (Delete)

## 입력값 검증

- 장비번호, 장비명 필수 입력 검사
- 장비번호 중복 등록 방지
- 입력 문자열 앞뒤 공백 제거
- 존재하지 않는 장비 접근/수정/삭제 시 404 오류 처리
- 데이터베이스 저장 실패 시 안내 메시지 표시
