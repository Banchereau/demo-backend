from fastapi import FastAPI

app = FastAPI(
    title="Demo Backend",
    description="Backend de démonstration DevSecOps Kubernetes",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Demo Backend running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/version")
def version():
    return {
        "application": "demo-backend",
        "version": "1.0.0"
    }
