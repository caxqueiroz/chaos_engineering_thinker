from fastapi import FastAPI
from app.routes.api import router

app = FastAPI(
    title="ChaosThinker",
    description="An AI-powered system analysis tool"
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
