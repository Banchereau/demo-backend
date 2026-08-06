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
    assert "Ingress Controller" in component_names

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


def test_platform_health_ingress_controller(monkeypatch, client):

    class MockDeploymentStatus:
        ready_replicas = 1

    class MockDeploymentSpec:
        replicas = 1

    class MockDeployment:
        status = MockDeploymentStatus()
        spec = MockDeploymentSpec()

    class MockAppsApi:

        def read_namespaced_deployment(
            self,
            name,
            namespace,
        ):
            assert name == "ingress-nginx-controller"
            assert namespace == "ingress-nginx"

            return MockDeployment()

    monkeypatch.setattr(
        "app.services.platform_health.get_apps_v1_api",
        lambda: MockAppsApi(),
    )

    response = client.get(
        "/health/platform"
    )

    assert response.status_code == 200

    data = response.json()

    ingress = next(
        component
        for component in data["components"]
        if component["name"] == "Ingress Controller"
    )

    assert ingress["status"] == "healthy"
    assert "1 controller running" in ingress["message"]


def test_platform_health_ingress_controller_degraded(
    monkeypatch,
    client,
):

    class MockDeploymentStatus:
        ready_replicas = 0

    class MockDeploymentSpec:
        replicas = 1

    class MockDeployment:
        status = MockDeploymentStatus()
        spec = MockDeploymentSpec()

    class MockAppsApi:

        def read_namespaced_deployment(
            self,
            name,
            namespace,
        ):
            return MockDeployment()

    monkeypatch.setattr(
        "app.services.platform_health.get_apps_v1_api",
        lambda: MockAppsApi(),
    )

    response = client.get(
        "/health/platform"
    )

    assert response.status_code == 200

    data = response.json()

    ingress = next(
        component
        for component in data["components"]
        if component["name"] == "Ingress Controller"
    )

    assert ingress["status"] == "degraded"
    assert "0/1 controllers ready" in ingress["message"]

def test_platform_health_applications(monkeypatch, client):

    from app.models.application import KubernetesApplication


    def mock_get_applications():

        return [
            KubernetesApplication(
                name="demo-backend",
                namespace="default",
                ingress="demo-backend",
                hosts=[
                    "api.example.com"
                ],
                service="demo-backend",
                deployment="demo-backend",
                desired_replicas=1,
                ready_replicas=1,
                pods=[
                    "demo-backend-xxxxx"
                ],
                status="healthy",
            ),
            KubernetesApplication(
                name="demo-frontend",
                namespace="default",
                ingress="demo-frontend",
                hosts=[
                    "app.example.com"
                ],
                service="demo-frontend",
                deployment="demo-frontend",
                desired_replicas=1,
                ready_replicas=1,
                pods=[
                    "demo-frontend-xxxxx"
                ],
                status="healthy",
            ),
        ]


    monkeypatch.setattr(
        "app.services.platform_health.get_applications",
        mock_get_applications,
    )


    response = client.get(
        "/health/platform"
    )

    assert response.status_code == 200

    data = response.json()

    applications = next(
        component
        for component in data["components"]
        if component["name"] == "Applications"
    )

    assert applications["status"] == "healthy"
    assert "2/2 applications healthy" in applications["message"]


def test_platform_health_applications_degraded(monkeypatch, client):

    from app.models.application import KubernetesApplication


    def mock_get_applications():

        return [
            KubernetesApplication(
                name="demo-backend",
                namespace="default",
                ingress=None,
                hosts=[],
                service="demo-backend",
                deployment="demo-backend",
                desired_replicas=1,
                ready_replicas=0,
                pods=[],
                status="degraded",
            ),
        ]


    monkeypatch.setattr(
        "app.services.platform_health.get_applications",
        mock_get_applications,
    )


    response = client.get(
        "/health/platform"
    )

    assert response.status_code == 200

    data = response.json()

    applications = next(
        component
        for component in data["components"]
        if component["name"] == "Applications"
    )

    assert applications["status"] == "degraded"
    assert "0/1 applications healthy" in applications["message"]


def test_platform_health_monitoring(client):

    response = client.get(
        "/health/platform"
    )

    assert response.status_code == 200

    data = response.json()

    monitoring = next(
        component
        for component in data["components"]
        if component["name"] == "Monitoring"
    )

    assert monitoring["status"] in [
        "healthy",
        "degraded",
    ]
