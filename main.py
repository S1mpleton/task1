from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import router_api
from infrastructure.database.config import create_db_and_tables


@asynccontextmanager
async def lifespan(app_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router_api)



if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
