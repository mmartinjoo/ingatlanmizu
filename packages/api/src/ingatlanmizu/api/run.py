import uvicorn
from fastapi import FastAPI
from ingatlanmizu.core.config import settings

app = FastAPI()

@app.get("/")
def hello():
    return "hello"

def main():
    uvicorn.run(
        "ingatlanmizu.api.run:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == 'local' else False,
    )