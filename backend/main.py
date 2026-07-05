from fastapi import FastAPI

app = FastAPI(
    title="JNAS OS",
    version="1.0.0",
    description="AI Operating System Backend"
)

@app.get("/")
def home():
    return {
        "status": "running",
        "project": "JNAS OS",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"health": "OK"}
