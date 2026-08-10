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
    labels: dict[str, str]
    annotations: dict[str, str]
    owner_references: list[dict[str, str | None]]


class PodRestart(BaseModel):
    container: str
    restart_count: int
    reason: str | None
    exit_code: int | None
    signal: int | None
    started_at: str | None
    finished_at: str | None
