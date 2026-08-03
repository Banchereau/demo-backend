from pydantic import BaseModel


class KubernetesEvent(BaseModel):
    namespace: str
    name: str
    type: str | None = None
    reason: str | None = None
    message: str | None = None
    involved_object: str | None = None
    timestamp: str | None = None
