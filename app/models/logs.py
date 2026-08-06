from pydantic import BaseModel


class PodLogs(BaseModel):
    namespace: str
    pod: str
    logs: str
