# main.py
from fastapi import FastAPI
from routes.auth_routes import router as auth_router
from routes.menu_routes import router as menu_router
from routes.order_routes import router as order_router
from routes.table_routes import router as table_router
from routes.inventory_routes import router as inventory_router
from routes.chat_routes import router as chat_router
from db.database import Base, engine  # ← ADD THIS
# ✅ ADD THIS — creates all tables on startup
from models import user_model, menu_model, order_model, table_model, inventory_model
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Restora API",
    description="Restaurant Management System API",
    version="1.0.0"
)

app.include_router(auth_router,      prefix="/auth",      tags=["Auth"])
app.include_router(menu_router,      prefix="/menu",      tags=["Menu"])
app.include_router(order_router,     prefix="/orders",    tags=["Orders"])
app.include_router(table_router,     prefix="/tables",    tags=["Tables"])
app.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
app.include_router(chat_router,      prefix="/chat" ,     tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Welcome to Restora API 🍽️"}