import uvicorn
from fastapi import FastAPI

from api import users_router, groups_router, tasks_router


app = FastAPI()

app.include_router(users_router)
app.include_router(groups_router)
app.include_router(tasks_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
