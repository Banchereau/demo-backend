from app.services.status import get_application_status


def test_application_status_healthy():
    assert get_application_status(1, 1) == "healthy"


def test_application_status_multiple_replicas():
    assert get_application_status(3, 3) == "healthy"


def test_application_status_degraded():
    assert get_application_status(3, 2) == "degraded"


def test_application_status_zero_replicas():
    assert get_application_status(0, 0) == "healthy"
