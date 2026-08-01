from pydantic import BaseModel


class Pod(BaseModel):
    name: str
    namespace: str
    status: str
    restarts: int
    node: str
    age: str
