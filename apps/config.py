from pathlib import Path

basedir = Path(__file__).parent.parent


class BaseConfig:
    SECRET_KEY = "2AZSMss3p5QPbcY2hBsJ"
    WTF_CSRF_SECRET_KEY = "AuwzyszU5sugKN7KZs6f"
    LABELS = [
        "unlabeled", "person", "bicycle", "car", "motorcycle", "airplane",
        "bus", "train", "truck", "boat", "traffic light", "fire hydrant",
        "street sign", "stop sign", "parking meter", "bench", "bird", "cat",
        "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
        "hat", "backpack", "umbrella", "shoe", "eye glasses", "handbag", "tie",
        "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
        "baseball bat", "baseball glove", "skateboard", "surfboard",
        "tennis racket", "bottle", "plate", "wine glass", "cup", "fork",
        "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
        "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
        "couch", "potted plant", "bed", "mirror", "dining table", "window",
        "desk", "toilet", "door", "tv", "laptop", "mouse", "remote",
        "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
        "refrigerator", "blender", "book", "clock", "vase", "scissors",
        "teddy bear", "hair drier", "toothbrush", "hair brush",
    ]


class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://flask:PythonDB@localhost:3306/flaskDB"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    UPLOAD_FOLDER = str(Path(basedir, "apps", "detector", "storage"))


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'testing.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


config = {
    "testing": TestingConfig,
    "local": LocalConfig,
}