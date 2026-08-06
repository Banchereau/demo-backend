from app.services.logs import get_pod_logs


def test_get_pod_logs(monkeypatch):

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

    result = get_pod_logs(
        "default",
        "demo-backend-12345",
    )

    assert result.namespace == "default"
    assert result.pod == "demo-backend-12345"

    assert "Application started" in result.logs
    assert "Listening on port 8000" in result.logs
