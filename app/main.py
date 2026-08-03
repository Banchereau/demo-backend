from fastapi import FastAPI

from app.api import cluster, health, pods, services, version, deployments, namespaces, events
from app.core import APP_NAME, APP_VERSION

app = FastAPI(
    title="Demo Backend",
    description="Backend de démonstration DevSecOps Kubernetes",
    version=APP_VERSION,
)


@app.get("/")
def root():
    return {
        "application": APP_NAME,
        "status": "running",
        "message": "Demo Backend running",
        "version": APP_VERSION,
    }


app.include_router(health.router)
app.include_router(version.router)
app.include_router(cluster.router)
app.include_router(pods.router)
app.include_router(services.router)
app.include_router(deployments.router)
app.include_router(namespaces.router)
app.include_router(events.router)
