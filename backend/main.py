from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, inventory, daily_sales, daily_expenses, investments, summary, one_time_expenses
import models
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(daily_sales.router)
app.include_router(daily_expenses.router)
app.include_router(investments.router)
app.include_router(summary.router)
app.include_router(one_time_expenses.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get('/health')
def health():
    return {"status": "ok"}
