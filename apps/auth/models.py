# apps/auth/models.py

from apps.app import login_manager
from apps.crud.models import User  # ★ 핵심: crud에서 정의된 User를 가져옵니다.

# [주의] 여기에는 class User(db.Model...): 코드가 절대 있으면 안 됩니다!
# 클래스 내부에 있던 @property, password.setter 등은 
# 이미 apps/crud/models.py의 User 클래스 안에 들어있어야 합니다.

@login_manager.user_loader
def load_user(user_id):
    # 로그인 사용자를 로드하는 기능만 남겨둡니다.
    return User.query.get(user_id)