from app.models.certificate import Certificate


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


from app.models.certificate import Certificate


def test_platform_health_certificates(monkeypatch, client):

    def mock_get_certificates():

        return [
            Certificate(
                namespace="default",
                name="demo-tls",
                secret_name="demo-tls",
                dns_names=[
                    "api.example.com"
                ],
                issuer="letsencrypt",
                ready=True,
                status="Certificate is up to date",
                not_after=None,
                renewal_time=None,
            )
        ]

    monkeypatch.setattr(
        "app.services.platform_health.get_certificates",
        mock_get_certificates,
    )

    response = client.get(
        "/health/platform"
    )

    assert response.status_code == 200

    data = response.json()

    cert_manager = next(
        component
        for component in data["components"]
        if component["name"] == "cert-manager"
    )

    assert cert_manager["status"] == "healthy"
    assert "1/1 certificates ready" in cert_manager["message"]
