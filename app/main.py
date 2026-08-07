from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import cluster, health, pods, services, version, deployments, namespaces, events, certificates, ingresses, applications, platform
from app.core import APP_NAME, APP_VERSION
from app.api.logs import router as logs_router

app = FastAPI(
    title="Demo Backend",
    description="Backend de démonstration DevSecOps Kubernetes",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://172.29.88.206:3000",
        "https://xcodewhisperer.fr",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(certificates.router)
app.include_router(ingresses.router)
app.include_router(applications.router)
app.include_router(platform.router)
app.include_router(logs_router)
