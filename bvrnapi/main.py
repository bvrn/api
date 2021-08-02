from fastapi import FastAPI

from bvrnapi.db import models
from bvrnapi.db.database import engine
from bvrnapi.routers import associations

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(associations.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000, workers=2)
