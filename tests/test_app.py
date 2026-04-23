def test_index(client):
	# 메인 페잊이 접속 테스트
	response = client.get("/")
	assert response.status_code == 200

def test_login_page(client):
	# 로그인 페이지 접속 테스트
	response = client.get("/auth/login")
	assert response.status_code == 200
