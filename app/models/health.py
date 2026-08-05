from pydantic import BaseModel
from typing import List


class HealthComponent(BaseModel):
    name: str
    status: str
    message: str


class PlatformHealth(BaseModel):
    status: str
    components: List[HealthComponent]
