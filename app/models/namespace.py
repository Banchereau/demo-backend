from pydantic import BaseModel


class KubernetesNamespace(BaseModel):
    name: str
    status: str


class NamespaceResponse(BaseModel):
    status: str
    namespaces: list[KubernetesNamespace]
    error: str | None = None
