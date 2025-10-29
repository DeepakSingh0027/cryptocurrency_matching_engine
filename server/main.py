from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import datetime
import logging
from server.engine.matcher import MatchingEngine

from server.api import routes, streams

#logging instance
logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title= 'Cryptocurrency Matching Engine',
    version = '1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Adding routers from api folder
app.include_router(routes.router , prefix="/appV1", tags=["REST API"])
app.include_router(streams.router , prefix="/wsV1", tags=["WebSocket API"])

#startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the Cryptocurrency Matching Engine...")
    app.state.engine = MatchingEngine(app=app)
    #market data connections management
    app.state.connections = []
    #for trade websockets management
    app.state.t_connections = []
    logger.info("Application startup at %s", datetime.datetime.now())

#shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the Cryptocurrency Matching Engine...")
    logger.info("Application shutdown at %s", datetime.datetime.now())

#Root endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service" : "Cryptocurrency Matching Engine",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    }


