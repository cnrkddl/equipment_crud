from flask import Flask, abort, redirect, render_template, url_for
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
            #장비가 없으면 실행을 즉시 중단시키고, 
            abort(404, description="해당 장비를 찾을 수 없습니다.")
            # 그 설명 문구가 담긴 404 응답을 바로 돌려줌
        return render_template("equipment_detail.html", equipment=equipment)

    return app  # 완성된 Flask 앱 객체 반환


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
