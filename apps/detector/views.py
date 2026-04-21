import random
import uuid
from pathlib import Path

import cv2
import numpy as np
import torchvision
from flask import Blueprint, abort, current_app, redirect, render_template, url_for, request, send_from_directory
from flask_login import current_user, login_required
from PIL import Image

from apps.app import db
from apps.crud.models import User
from apps.detector.forms import UploadImageForm, SearchForm
from apps.detector.models import UserImage, UserImageTag

dt = Blueprint(
    "detector",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/detector/static",
)


@dt.route("/")
def index():
    search_form = SearchForm()

    # UserImage를 기준으로 모든 이미지를 가져옵니다.
    # (작성자 정보는 모델의 relationship을 통해 템플릿에서 바로 쓸 수 있습니다.)
    user_images = (
        db.session.query(UserImage)
        .order_by(UserImage.created_at.desc())
        .all()
    )
    
    return render_template(
        "detector/index.html",
        user_images=user_images,
        search_form=search_form,
    )


@dt.route("/images/search", methods=["GET"])
def search():
    # request.args를 통해 검색어를 가져옵니다.
    search_form = SearchForm(request.args)
    query = search_form.search_text.data
    
    # 쿼리 시작
    user_images_query = db.session.query(User, UserImage).join(UserImage, User.id == UserImage.user_id)
    
    if query:
        # 태그 테이블과 조인하여 검색어 필터링
        user_images = (
            user_images_query.join(UserImageTag, UserImage.id == UserImageTag.user_image_id)
            .filter(UserImageTag.tag_name.like(f"%{query}%"))
            .all()
        )
    else:
        # 검색어가 없으면 전체 목록 반환
        user_images = user_images_query.all()
    
    return render_template(
        "detector/index.html",
        user_images=user_images,
        search_form=search_form,
    )


@dt.route("/images/new", methods=["GET", "POST"])
@login_required
def upload_image():
    form = UploadImageForm()
    if form.validate_on_submit():
        file = form.image.data
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext
        image_path = Path(current_app.config["UPLOAD_FOLDER"], image_uuid_file_name)
        file.save(image_path)
        user_image = UserImage(
            user_id=current_user.id,
            image_path=image_uuid_file_name,
        )
        db.session.add(user_image)
        db.session.commit()
        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)

@dt.route("/images/<path:filename>")
def get_image(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


def make_color(labels):
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    return random.choice(colors)


def make_line(result_image):
    return round(0.002 * max(result_image.shape[0:2])) + 1


def draw_lines(c1, c2, result_image, line, color):
    cv2.rectangle(result_image, c1, c2, color, thickness=line)


def draw_texts(result_image, line, c1, color, labels, label):
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [225, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )


def exec_detect(target_image_path):
    labels = current_app.config["LABELS"]
    image = Image.open(target_image_path)
    image_tensor = torchvision.transforms.functional.to_tensor(image)
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    model.eval()
    output = model([image_tensor])[0]
    tags = []
    result_image = np.array(image.convert("RGB"))

    for box, label, score in zip(output["boxes"], output["labels"], output["scores"]):
        if score > 0.5 and label < len(labels):
            color = make_color(labels)
            line = make_line(result_image)
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))
            draw_lines(c1, c2, result_image, line, color)
            draw_texts(result_image, line, c1, color, labels, label)
            tags.append(labels[label])

    detected_image_file_name = str(uuid.uuid4()) + ".jpg"
    detected_image_file_path = str(
        Path(current_app.config["UPLOAD_FOLDER"], detected_image_file_name)
    )
    cv2.imwrite(detected_image_file_path, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))
    return tags, detected_image_file_name


def save_detected_image_tags(user_image, tags, detected_image_file_name):
    user_image.image_path = detected_image_file_name
    user_image.is_detected = True
    db.session.add(user_image)
    for tag in tags:
        user_image_tag = UserImageTag(user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)
    db.session.commit()


@dt.route("/images/detect/<string:image_id>", methods=["POST"])
@login_required
def detect(image_id):
    user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()
    if user_image is None:
        abort(404)
    target_image_path = Path(current_app.config["UPLOAD_FOLDER"], user_image.image_path)
    tags, detected_image_file_name = exec_detect(target_image_path)
    save_detected_image_tags(user_image, tags, detected_image_file_name)
    return redirect(url_for("detector.index"))


@dt.route("/images/delete/<string:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()
    if user_image is None:
        abort(404)
    db.session.query(UserImageTag).filter(
        UserImageTag.user_image_id == image_id
    ).delete()
    db.session.delete(user_image)
    db.session.commit()
    return redirect(url_for("detector.index"))



# 커스텀 오류 핸들러
@dt.app_errorhandler(404)
def page_not_found(e):
    return render_template("detector/404.html"), 404


@dt.app_errorhandler(500)
def internal_server_error(e):
    return render_template("detector/500.html"), 500