from flask import Flask, abort, flash, redirect, render_template, request, url_for
from models import Equipment, db

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

    # "/equipment/create" 접속 시 실행되는 라우트
    @app.route("/equipment/create", methods=["GET", "POST"])
    def equipment_create():
        # 검증 실패 시 입력값과 에러 메시지를 그대로 담아 폼을 다시 보여줌
        def render_form_error(error):
            return render_template(
                "equipment_create.html", form=request.form, error=error
            )

        if request.method == "POST":
            # 지시서 9번 요구사항: 모든 입력 문자열은 앞뒤 공백을 제거해서 저장
            equipment_code = request.form.get("equipment_code", "").strip()
            name = request.form.get("name", "").strip()
            location = request.form.get("location", "").strip()
            status = request.form.get("status", "").strip()
            description = request.form.get("description", "").strip()

            # 장비번호 필수 입력 검증
            if not equipment_code:
                return render_form_error("장비번호는 필수입니다")

            # 장비명 필수 입력 검증
            if not name:
                return render_form_error("장비명은 필수입니다")

            # 장비번호 중복 등록 방지: DB 커밋 전에 먼저 조회해서 UNIQUE 제약으로 죽지 않고 안내 메시지로 처리
            existing = Equipment.query.filter_by(
                equipment_code=equipment_code
            ).first()

            if existing is not None:
                return render_form_error("이미 등록된 장비번호입니다")

            equipment = Equipment(
                equipment_code=equipment_code,
                name=name,
                location=location,
                status=status,
                description=description,
            )
            db.session.add(equipment)
            try:
                db.session.commit()
            except Exception:
                # DB 저장 실패 시에도 프로그램이 죽지 않고 안내 메시지를 보여줌 
                db.session.rollback()
                return render_form_error("저장 중 오류가 발생했습니다")

            flash("등록이 완료되었습니다")  # 목록 화면에서 get_flashed_messages()로 표시됨
            return redirect(url_for("equipment_list"))
        return render_template("equipment_create.html")

    return app  # 완성된 Flask 앱 객체 반환


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
