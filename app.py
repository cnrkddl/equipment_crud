from flask import Flask, abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from models import Equipment, db

# 등록/수정 폼의 선택지와 목록/상세 화면의 상태 뱃지 색상이 이 목록 하나를 같이 참조한다.
# (DB 스키마가 아닌 화면 표시 관심사이므로 models.py가 아닌 여기에 둔다)
EQUIPMENT_STATUSES = ["정상", "점검중", "고장"]
STATUS_STYLE_MAP = {"정상": "ok", "점검중": "pending", "고장": "fault"}


def status_style(status):
    return STATUS_STYLE_MAP.get(status, "pending")


def validate_equipment_form(form, exclude_id=None):
    # 모든 입력 문자열은 앞뒤 공백을 제거해서 저장
    data = {
        "equipment_code": form.get("equipment_code", "").strip(),
        "name": form.get("name", "").strip(),
        "location": form.get("location", "").strip(),
        "status": form.get("status", "").strip(),
        "description": form.get("description", "").strip(),
    }

    if not data["equipment_code"]:
        return None, "장비번호는 필수입니다"
    if not data["name"]:
        return None, "장비명은 필수입니다"

    # 장비번호 중복 등록 방지 (edit에서는 자기 자신은 제외하고 검사)
    query = Equipment.query.filter_by(equipment_code=data["equipment_code"])
    if exclude_id is not None:
        query = query.filter(Equipment.id != exclude_id)
    if query.first() is not None:
        return None, "이미 등록된 장비번호입니다"

    return data, None


def commit_or_rollback(log_label):
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"[DB 오류] {log_label}: {e}")
        return False


# 매번 새 Flask 앱을 만들어서 반환하기 때문에,
# 평소 실행과 테스트가 서로 다른 설정으로
def create_app(test_config=None):
    app = Flask(__name__)  # Flask 앱 객체 생성

    # DB 파일 위치, 세션 암호화 등에 쓰이는 key 설정
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///equipment.db"
    app.config["SECRET_KEY"] = "dev"

    if test_config:
        app.config.update(test_config)

    # db를 이 Flask 앱과 실제로 연결
    db.init_app(app)

    # 상태 목록/뱃지 색상 매핑을 모든 템플릿에서 같은 곳(위 상수)을 참조하게 함
    @app.context_processor
    def inject_equipment_constants():
        return dict(equipment_statuses=EQUIPMENT_STATUSES, status_style=status_style)

    # "/" 접속 시 "/equipment"로 리다이렉트
    @app.route("/")
    def index():
        return redirect(url_for("equipment_list"))

    # "/equipment" 접속 시 실행되는 라우트
    @app.route("/equipment")
    def equipment_list():
        equipments = Equipment.query.all()  # equipment 테이블 전체 조회
        return render_template("equipment_list.html", equipments=equipments)

    # "/equipment/<id>" 접속 시 실행되는 라우트
    # <int:id> : 컨버터
    @app.route("/equipment/<int:id>") #이 위치에 정수가 들어오면 id라는 이름으로 받겠다는 뜻
    def equipment_detail(id):
        equipment = db.session.get(Equipment, id) #있으면 equipment반환 , 없으면 none
        if equipment is None:
            #장비가 없으면 실행을 즉시 중단
            abort(404, description="해당 장비를 찾을 수 없습니다.")
            #설명 문구가 담긴 404 응답을 바로 돌려줌
        return render_template("equipment_detail.html", equipment=equipment)

    # "/equipment/<id>/edit" 접속 시 실행되는 라우트
    # GET: 수정 폼에 기존 값 표시
    # POST: 폼 제출된 내용으로 기존 장비 정보 수정
    @app.route("/equipment/<int:id>/edit", methods=["GET", "POST"])
    def equipment_edit(id):
        equipment = db.session.get(Equipment, id)
        if equipment is None:
            abort(404, description="해당 장비를 찾을 수 없습니다.")

        if request.method == "POST":
            data, error = validate_equipment_form(request.form, exclude_id=equipment.id)
            if error:
                flash(error, "error")
                # 검증 실패 시 방금 제출한 값을 그대로 폼에 다시 보여줌 (DB에 저장된 이전 값이 아님)
                return render_template(
                    "equipment_edit.html", equipment=equipment, form=request.form
                )

            equipment.equipment_code = data["equipment_code"]
            equipment.name = data["name"]
            equipment.location = data["location"]
            equipment.status = data["status"]
            equipment.description = data["description"]

            if not commit_or_rollback(f"장비 수정 실패 (id={id})"):
                flash("저장 중 오류가 발생했습니다", "error")
                return render_template(
                    "equipment_edit.html", equipment=equipment, form=request.form
                )

            return redirect(url_for("equipment_list"))
        return render_template("equipment_edit.html", equipment=equipment)

    # "/equipment/<id>/delete" 접속 시 실행되는 라우트
    # POST 요청만 허용, 삭제 완료 후 목록 화면으로 이동
    @app.route("/equipment/<int:id>/delete", methods=["POST"])
    def equipment_delete(id):
        equipment = db.session.get(Equipment, id)
        if equipment is None:
            abort(404, description="해당 장비를 찾을 수 없습니다.")

        db.session.delete(equipment)
        if not commit_or_rollback(f"장비 삭제 실패 (id={id})"):
            flash("삭제 중 오류가 발생했습니다", "error")
            return redirect(url_for("equipment_detail", id=id))

        return redirect(url_for("equipment_list"))

    # "/equipment/create" 접속 시 실행되는 라우트
    # GET: 빈 등록 폼 보여주기
    # POST : 폼 제출하기
    @app.route("/equipment/create", methods=["GET", "POST"])
    def equipment_create():
        # 검증 실패 시 입력값을 그대로 담아 폼을 다시 보여줌 (에러는 flash로 표시)
        def render_form_error(error):
            flash(error, "error")
            return render_template("equipment_create.html", form=request.form)

        if request.method == "POST":
            data, error = validate_equipment_form(request.form)
            if error:
                return render_form_error(error)

            equipment = Equipment(**data)
            db.session.add(equipment)
            if not commit_or_rollback("장비 등록 실패"):
                return render_form_error("저장 중 오류가 발생했습니다")

            flash("등록이 완료되었습니다")
            # 사용자를 목록 페이지로 이동시킴
            return redirect(url_for("equipment_list"))
        return render_template("equipment_create.html")

    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
