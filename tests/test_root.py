def test_root(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "demo-backend"
    assert data["status"] == "running"
    assert data["message"] == "Demo Backend running"
    assert data["version"] == "1.0.0"
