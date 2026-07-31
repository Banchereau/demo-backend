from pydantic import BaseModel


class ClusterStatus(BaseModel):
    nodes: int
    pods: int
    services: int
    namespaces: int
    health: str


class ClusterError(BaseModel):
    health: str
    error: str
