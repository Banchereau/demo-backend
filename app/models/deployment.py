from pydantic import BaseModel


class Deployment(BaseModel):
    name: str
    namespace: str
    replicas: int
    ready_replicas: int
    available_replicas: int
    strategy: str
    images: str
