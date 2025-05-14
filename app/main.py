from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .api import router
from .database import engine, Base

app = FastAPI(
    title="Whalebone Microservice",
    description="A simple microservice with REST API endpoints",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Create database tables
Base.metadata.create_all(bind=engine)


app.include_router(router)


# Let's redirect default/root to the interactive docs
@app.get("/")
def root():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
