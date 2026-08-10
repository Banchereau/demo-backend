from datetime import datetime

from pydantic import BaseModel


class Deployment(BaseModel):
    name: str
    namespace: str
    replicas: int
    ready_replicas: int
    available_replicas: int
    strategy: str
    images: str


class RolloutRevision(BaseModel):
    revision: int
    replicas: int
    ready_replicas: int
    image: str
    created_at: datetime | None
    is_current: bool
