from fastapi import FastAPI


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
