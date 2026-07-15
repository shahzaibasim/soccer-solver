from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.soccer import soccer_router
from app.core.main_router import router as main_router
from app.core.logger import init_logging

root_router = APIRouter()

app = FastAPI(
    title="Soccer Solver API",
    description=(
        "Player search, contextualised profile analysis, "
        "and transfer value simulation for soccer managers."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
app.include_router(soccer_router)
app.include_router(root_router)

init_logging()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
