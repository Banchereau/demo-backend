def test_platform_health(client):
    response = client.get("/health/platform")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert data["status"] in [
        "healthy",
        "degraded",
    ]

    assert "components" in data
    assert len(data["components"]) > 0

    component_names = [
        component["name"]
        for component in data["components"]
    ]

    assert "Kubernetes API" in component_names
    assert "cert-manager" in component_names
    assert "FluxCD" in component_names
