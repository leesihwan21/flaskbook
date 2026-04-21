from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField, SubmitField


class UploadImageForm(FlaskForm):
    image = FileField(
        validators=[
            FileRequired("이미지 파일을 선택해주세요."),
            FileAllowed(["png", "jpg", "jpeg"], "png, jpg, jpeg 파일만 업로드 가능합니다."),
        ]
    )
    submit = SubmitField("업로드")


class DetectorForm(FlaskForm):
    submit = SubmitField("감지")


class DeleteForm(FlaskForm):
    submit = SubmitField("삭제")


class SearchForm(FlaskForm):
    search_text = StringField("태그 검색")
    submit = SubmitField("검색")