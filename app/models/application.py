from pydantic import BaseModel


class KubernetesApplication(BaseModel):
    name: str
    namespace: str

    ingress: str | None = None
    hosts: list[str] = []

    service: str | None = None

    deployment: str | None = None

    desired_replicas: int = 0
    ready_replicas: int = 0

    pods: list[str] = []

    certificate: str | None = None

    status: str = "unknown"


#
# Application detail view
#

class DeploymentDetail(BaseModel):
    name: str
    desired_replicas: int
    ready_replicas: int
    image: str | None = None


class ServiceDetail(BaseModel):
    name: str
    type: str | None = None
    cluster_ip: str | None = None


class IngressDetail(BaseModel):
    name: str
    hosts: list[str] = []
    tls: bool = False


class PodDetail(BaseModel):
    name: str
    status: str
    restarts: int = 0


class CertificateDetail(BaseModel):
    name: str
    ready: bool = False
    expiration: str | None = None


class ApplicationDetail(BaseModel):
    name: str
    namespace: str

    status: str

    deployment: DeploymentDetail | None = None
    service: ServiceDetail | None = None
    ingress: IngressDetail | None = None

    pods: list[PodDetail] = []

    certificates: list[CertificateDetail] = []
