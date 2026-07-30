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

        nodes = v1.list_node()
        pods = v1.list_pod_for_all_namespaces()
        services = v1.list_service_for_all_namespaces()
        namespaces = v1.list_namespace()

        return {
            "nodes": len(nodes.items),
            "pods": len(pods.items),
            "services": len(services.items),
            "namespaces": len(namespaces.items),
            "health": "healthy",
        }

    except Exception as e:
        return {
            "health": "unhealthy",
            "error": str(e)
        }
