from datetime import datetime
from pydantic import BaseModel


class Certificate(BaseModel):
    namespace: str
    name: str
    secret_name: str
    dns_names: list[str]
    issuer: str | None = None
    ready: bool
    status: str
    not_after: datetime | None = None
    renewal_time: datetime | None = None
