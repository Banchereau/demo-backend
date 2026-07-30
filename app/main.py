from fastapi import FastAPI
from kubernetes import client, config

APP_NAME = "demo-backend"
APP_VERSION = "1.0.0"

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


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/version")
def version():
    return {
        "application": APP_NAME,
        "version": APP_VERSION
    }


@app.get("/cluster")
def cluster():
    try:
        config.load_incluster_config()

        v1 = client.CoreV1Api()

        v1.get_api_resources()

        return {
            "connected": True
        }

    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }
