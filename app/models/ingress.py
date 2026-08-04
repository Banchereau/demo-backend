from pydantic import BaseModel


class KubernetesIngress(BaseModel):
    namespace: str
    name: str
    hosts: list[str]
    service: str | None = None
    tls_secret: str | None = None
