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

## 폴더 구조

```
equipment_crud/
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── instance/
│   └── equipment.db
├── templates/
│   ├── base.html
│   ├── equipment_list.html
│   ├── equipment_detail.html
│   ├── equipment_create.html
│   └── equipment_edit.html
└── static/
    └── style.css
```

## 기능

- 장비 등록 (Create)
- 장비 목록 조회 (Read)
- 장비 상세 조회 (Read)
- 장비 정보 수정 (Update)
- 장비 삭제 (Delete)
