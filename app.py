from flask import Flask, redirect, url_for

from models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///equipment.db"
app.config["SECRET_KEY"] = "dev"

db.init_app(app)


@app.route("/")
def index():
    return redirect(url_for("equipment_list"))


@app.route("/equipment")
def equipment_list():
    return "장비 목록 화면 (구현 예정)"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
