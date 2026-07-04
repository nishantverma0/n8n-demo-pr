from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.config import settings
from app.observability import tracing  # noqa: F401 (side-effect: enables LangSmith)
from app.graph.checkpoints import init_checkpointer
from app.api.v1 import (routes_company, routes_agents, routes_chat,
                        routes_approvals, routes_simulation, routes_ml, routes_metrics)
from app.api.ws import agent_stream

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_checkpointer()   # creates LangGraph checkpoint tables once
    yield

app = FastAPI(title="AI Business Simulator", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(routes_company.router, prefix=PREFIX, tags=["companies"])
app.include_router(routes_agents.router, prefix=PREFIX, tags=["agents"])
app.include_router(routes_chat.router, prefix=PREFIX, tags=["chat"])
app.include_router(routes_approvals.router, prefix=PREFIX, tags=["approvals"])
app.include_router(routes_simulation.router, prefix=PREFIX, tags=["simulations"])
app.include_router(routes_ml.router, prefix=PREFIX, tags=["ml"])
app.include_router(routes_metrics.router, prefix=PREFIX, tags=["metrics"])
app.include_router(agent_stream.router, prefix=PREFIX, tags=["ws"])

app.mount("/prometheus", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.env}
