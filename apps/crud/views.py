from apps.app import db
from apps.crud.forms import UserForm
from apps.crud.models import User
from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required

# Blueprint로 crud 앱 생성
crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)


# index 엔드포인트를 작성하고 index.html 반환
@crud.route("/")
@login_required
def index():
    return render_template("crud/index.html")


@crud.route("/sql")
@login_required
def sql():
    db.session.query(User).all()
    return "콘솔 로그를 확인해 주세요."


@crud.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    # UserForm 인스턴스화
    form = UserForm()

    # 폼 값을 검증
    if form.validate_on_submit():
        # 사용자 생성
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )

        # 사용자 추가 후 커밋
        db.session.add(user)
        db.session.commit()

        # 사용자 목록 화면으로 리다이렉트
        return redirect(url_for("crud.users"))
    return render_template("crud/create.html", form=form)


@crud.route("/users")
@login_required
def users():
    """사용자 목록을 가져온다"""
    users = User.query.all()
    return render_template("crud/index.html", users=users)


# methods에 GET과 POST 지정
@crud.route("/users/<user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    form = UserForm()

    # User 모델을 이용하여 사용자 조회
    user = User.query.filter_by(id=user_id).first()

    # 폼이 서브밋된 경우 사용자를 업데이트하고 목록 화면으로 리다이렉트
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))

    # GET 요청인 경우 수정 화면(HTML) 반환
    return render_template("crud/edit.html", user=user, form=form)


@crud.route("/users/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("crud.users"))