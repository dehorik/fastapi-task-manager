from fastapi import FastAPI

from api import users_router, groups_router, tasks_router
from auth import auth_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(groups_router)
app.include_router(tasks_router)
