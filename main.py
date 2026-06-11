from app.database import Base, engine
from app import models
from fastapi import FastAPI
from app.routers.tasks import router as tasks_router
from app.routers.users import router as users_router

app = FastAPI(title="Tasks API")
Base.metadata.create_all(bind=engine)

app.include_router(tasks_router)
app.include_router(users_router)

@app.get("/")
def read_root():
    return {"message": "Tasks API is running"}
