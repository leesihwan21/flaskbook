from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class SignUpForm(FlaskForm):
    username = StringField(
        "사용자 이름",
        validators=[
            DataRequired("사용자 이름은 필수입니다."),
            Length(1, 30, "30자 이내로 입력해 주세요."),
        ],
    )
    email = StringField(
        "메일 주소",
        validators=[
            DataRequired("메일 주소는 필수입니다."),
            Email("메일 주소 형식으로 입력해 주세요."),
        ],
    )
    password = PasswordField("비밀번호", validators=[DataRequired("비밀번호는 필수입니다.")])
    submit = SubmitField("가입하기")


class LoginForm(FlaskForm):
    email = StringField(
        "메일 주소",
        validators=[
            DataRequired("메일 주소는 필수입니다."),
            Email("메일 주소 형식으로 입력해 주세요."),
        ],
    )
    password = PasswordField("비밀번호", validators=[DataRequired("비밀번호는 필수입니다.")])
    submit = SubmitField("로그인")

class FindIdForm(FlaskForm):
    username = StringField(
        "사용자 이름",
        validators=[
            DataRequired("사용자 이름은 필수입니다."),
            Length(1, 30, "30자 이내로 입력해 주세요."),
        ],
    )
    submit = SubmitField("아이디 찾기")

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        "메일 주소",
        validators=[
            DataRequired("메일 주소는 필수입니다."),
            Email("메일 주소 형식으로 입력해 주세요."),
        ],
    )
    submit = SubmitField("비밀번호 재설정 요청")
    
