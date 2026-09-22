import os

from dotenv import load_dotenv
from flask import Flask, Response, abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import ImmutableMultiDict

from models import Equipment, db

load_dotenv()

EQUIPMENT_STATUSES = ["정상", "점검중", "고장"]
STATUS_STYLE_MAP = {"정상": "ok", "점검중": "pending", "고장": "fault"}


def status_style(status: str) -> str:
    return STATUS_STYLE_MAP.get(status, "pending")  # 매핑에 없는 값이면 pending


# TODO : 형식 지정 & 출력 힌트 (return)
def validate_equipment_form(
    form: ImmutableMultiDict[str, str], exclude_id: int | None = None
) -> tuple[dict[str, str] | None, str | None]:
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


# id로 장비를 조회하고, 없으면 404 처리까지 함께 담당
def get_equipment_or_404(id: int) -> Equipment:
    equipment = db.session.get(Equipment, id) # 있으면 equipment 반환, 없으면 none 반환
    if equipment is None: # 장비가 없으면 실행을 즉시 중단
        abort(404, description="해당 장비를 찾을 수 없습니다.") # 설명 문구가 담긴 404 응답을 바로 돌려줌
    return equipment


# 검증/저장 실패 시 방금 제출한 값을 그대로 폼에 다시 보여줌 (DB에 저장된 이전 값이 아님)
def render_form_error(template: str, error: str, **context) -> str: #렌더링할 템플릿 파일명 , 에러메세지 문자열, 딕셔너리 매개변수
    # create안에서는 form만 있으면 되는데 edit에서는 form도 있고 equipment도 넘겨야해서 파라미터 개수 차이 존재 -> 여분의 키워드 인자 사용
    flash(error, "error") # 카테고리를 error로 고정하고 에러 메시지를 담아서 반환
    return render_template(template, form=request.form, **context) # 어떤 템플릿을 렌더링할지, 사용자가 방금 제출했던 폼 데이터를 템플릿에 넘겨 채움 


# 예외처리 함수 지정
def commit_or_rollback(log_label: str) -> bool:
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:  # 구체적인 예외 클래스 지정
        db.session.rollback()
        print(f"[DB 오류] {log_label}: {e}")  # 어떤 상황에서 무슨 에러인지 콘솔에 출력
        return False


# 매번 새 Flask 앱을 만들어서 반환하기 때문에,
# 평소 실행과 테스트가 서로 다른 설정으로
def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)  # Flask 앱 객체 생성

    # DB 파일 위치, 세션 암호화 등에 쓰이는 key 설정
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///equipment.db"
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    if test_config:
        app.config.update(test_config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY environment variable is not set")

    # db를 이 Flask 앱과 실제로 연결
    db.init_app(app)

    # 상태 목록/뱃지 색상 매핑을 모든 템플릿에서 같은 곳(위 상수)을 참조하게 함
    @app.context_processor
    def inject_equipment_constants() -> dict:
        return dict(equipment_statuses=EQUIPMENT_STATUSES, status_style=status_style)

    # "/" 접속 시 "/equipment"로 리다이렉트
    @app.route("/")
    def index() -> Response:
        return redirect(url_for("equipment_list"))

    # "/equipment" 접속 시 실행되는 라우트
    @app.route("/equipment")
    def equipment_list() -> str:
        equipments = Equipment.query.all()  # equipment 테이블 전체 조회
        return render_template("equipment_list.html", equipments=equipments)

    # "/equipment/<id>" 접속 시 실행되는 라우트
    # <int:id> : 컨버터
    @app.route("/equipment/<int:id>") #이 위치에 정수가 들어오면 id라는 이름으로 받겠다는 뜻
    def equipment_detail(id: int) -> str:
        equipment = get_equipment_or_404(id)
        return render_template("equipment_detail.html", equipment=equipment)

    # "/equipment/<id>/edit" 접속 시 실행되는 라우트
    # GET: 수정 폼에 기존 값 표시
    # POST: 폼 제출된 내용으로 기존 장비 정보 수정
    @app.route("/equipment/<int:id>/edit", methods=["GET", "POST"])
    def equipment_edit(id: int) -> str | Response:
        equipment = get_equipment_or_404(id)

        if request.method == "POST":
            data, error = validate_equipment_form(request.form, exclude_id=equipment.id)
            if error:
                return render_form_error("equipment_edit.html", error, equipment=equipment)

            equipment.equipment_code = data["equipment_code"]
            equipment.name = data["name"]
            equipment.location = data["location"]
            equipment.status = data["status"]
            equipment.description = data["description"]

            if not commit_or_rollback(f"장비 수정 실패 (id={id})"):
                return render_form_error(
                    "equipment_edit.html", "저장 중 오류가 발생했습니다", equipment=equipment
                )

            return redirect(url_for("equipment_list"))  # 수정 성공 시 장비 목록 페이지로 이동
        # GET 요청 시: 수정 페이지 진입 시 기존 값을 폼에 채워서 보여줌
        return render_template("equipment_edit.html", equipment=equipment)

    # "/equipment/<id>/delete" 접속 시 실행되는 라우트
    # POST 요청만 허용, 삭제 완료 후 목록 화면으로 이동
    @app.route("/equipment/<int:id>/delete", methods=["POST"])
    def equipment_delete(id: int) -> Response:
        equipment = get_equipment_or_404(id)

        db.session.delete(equipment)
        if not commit_or_rollback(f"장비 삭제 실패 (id={id})"):
            flash("삭제 중 오류가 발생했습니다", "error")
            return redirect(url_for("equipment_detail", id=id))

        return redirect(url_for("equipment_list"))

    # "/equipment/create" 접속 시 실행되는 라우트
    # GET: 빈 등록 폼 보여주기
    # POST : 폼 제출하기
    @app.route("/equipment/create", methods=["GET", "POST"])
    def equipment_create() -> str | Response:
        if request.method == "POST":
            data, error = validate_equipment_form(request.form)
            if error:
                return render_form_error("equipment_create.html", error)

            equipment = Equipment(**data)
            db.session.add(equipment)
            if not commit_or_rollback("장비 등록 실패"):
                return render_form_error("equipment_create.html", "저장 중 오류가 발생했습니다")

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
