from pydantic import BaseModel


class Pod(BaseModel):
    name: str
    namespace: str
    status: str
    restarts: int
    node: str
    age: str


class PodDetail(BaseModel):
    name: str
    namespace: str
    status: str
    restarts: int
    node: str | None
    age: str
    pod_ip: str | None
    host_ip: str | None
    service_account: str | None
    containers: list[str]
    images: list[str]
