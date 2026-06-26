from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.controllers.AuthenticationController import router as authentication_router
from backend.controllers.GameController import router as game_router
from backend.controllers.UserController import router as user_router
from backend.adapters.implementations.DatabaseInitializer import ensure_database_schema

import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    ensure_database_schema()


@app.get("/")
def read_root():
    return {"mensaje": "Servidor activo"}

app.include_router(authentication_router)
app.include_router(user_router)
app.include_router(game_router)

if __name__ == "__main__":
    # Arranca uvicorn desde Python
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1", 
        port=8000, 
        reload=True
    )
