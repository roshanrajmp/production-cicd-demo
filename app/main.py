from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Production CI/CD pipeline",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {
        "message": "Production CI/CD pipeline",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/version")
def version():
    return {
        "version": "1.0.0"
    }
