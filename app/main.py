from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, listings, requests

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CampusCart API",
    description="A marketplace API for students to buy and sell used textbooks, "
    "electronics, and other items within their college/hostel.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(requests.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "CampusCart API"}
