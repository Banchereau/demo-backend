from fastapi.testclient import TestClient


def test_pod_logs_endpoint(monkeypatch, client: TestClient):

    class MockCoreApi:

        def read_namespaced_pod_log(
            self,
            name,
            namespace,
            **kwargs,
        ):
            assert name == "demo-backend-12345"
            assert namespace == "default"

            assert kwargs["tail_lines"] == 200
            assert kwargs["timestamps"] is False
            assert kwargs["previous"] is False
            assert kwargs["container"] is None

            return (
                "INFO Application started\n"
                "INFO Connected database\n"
                "INFO Listening on port 8000\n"
            )

    monkeypatch.setattr(
        "app.services.logs.get_core_v1",
        lambda: MockCoreApi(),
    )

    response = client.get(
        "/pods/default/demo-backend-12345/logs"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["namespace"] == "default"
    assert data["pod"] == "demo-backend-12345"

    assert "Application started" in data["logs"]
    assert "Listening on port 8000" in data["logs"]


def test_pod_logs_endpoint_with_parameters(monkeypatch, client):

    class MockCoreApi:

        def read_namespaced_pod_log(
            self,
            name,
            namespace,
            **kwargs,
        ):
            assert name == "demo-backend-12345"
            assert namespace == "default"

            assert kwargs["tail_lines"] == 50
            assert kwargs["timestamps"] is True
            assert kwargs["previous"] is True
            assert kwargs["container"] == "backend"

            return "previous container logs"

    monkeypatch.setattr(
        "app.services.logs.get_core_v1",
        lambda: MockCoreApi(),
    )

    response = client.get(
        "/pods/default/demo-backend-12345/logs"
        "?tail=50"
        "&timestamps=true"
        "&previous=true"
        "&container=backend"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["logs"] == "previous container logs"


def test_pod_logs_kubernetes_error(monkeypatch, client):

    class MockCoreApi:

        def read_namespaced_pod_log(
            self,
            *args,
            **kwargs,
        ):
            raise Exception("Kubernetes unavailable")

    monkeypatch.setattr(
        "app.services.logs.get_core_v1",
        lambda: MockCoreApi(),
    )

    response = client.get(
        "/pods/default/demo-backend-12345/logs"
    )

    assert response.status_code == 500


def test_pod_logs_not_found(client, monkeypatch):

    from kubernetes.client.exceptions import ApiException

    class MockCoreApi:

        def read_namespaced_pod_log(self, *args, **kwargs):
            raise ApiException(
                status=404,
                reason="Not Found",
            )

    monkeypatch.setattr(
        "app.services.logs.get_core_v1",
        lambda: MockCoreApi(),
    )

    response = client.get(
        "/pods/default/does-not-exist/logs"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Pod not found"
