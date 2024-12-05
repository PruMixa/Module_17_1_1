from fastapi import FastAPI
from app.routers import task
from app.routers import user
from app.backend.db import Base, engine


app = FastAPI()


@app.get("/")
async def welcome():
    return {"message": "Welcome to Taskmanager"}

# Base.metadata.create_all(bind=engine)
# print("Таблицы созданы (если они отсутствовали).")

app.include_router(user.router)
app.include_router(task.router)
