from pydantic import BaseModel


class Service(BaseModel):
    name: str
    namespace: str
    type: str
    cluster_ip: str
    ports: str
