from pydantic import BaseModel


class KubernetesApplication(BaseModel):
    name: str
    namespace: str

    ingress: str | None = None
    hosts: list[str] = []

    service: str | None = None

    deployment: str | None = None

    desired_replicas: int = 0
    ready_replicas: int = 0
    replicas: int = 0

    pods: list[str] = []

    certificate: str | None = None

    status: str = "unknown"
