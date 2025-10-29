from fastapi import APIRouter, HTTPException, WebSocket
import logging

logger = logging.getLogger("uvicorn.error")

router = APIRouter()

# WebSocket endpoint for market data updates
@router.websocket("/marketdata")
async def market_data_stream(websocket: WebSocket):
    try:
        await websocket.accept()
        connections = websocket.app.state.connections
        connections.append(websocket)
        logger.info("Connected to Market Data Stream. \n Ready for Streaming Market Data...")
        try:
            while True:
                await websocket.receive_text()
        except:
            connections.remove(websocket)
    except:
        raise HTTPException(status_code=400, detail="WebSocket connection failed")
    

# WebSocket endpoint for trade updates
@router.websocket("/trades")
async def trade_stream(websocket: WebSocket):
    try:
        await websocket.accept()
        t_connections = websocket.app.state.t_connections
        logger.info("Connected to Trades Stream. \n Ready for Streaming Trades Data...")
        t_connections.append(websocket)
        try:
            while True:
                await websocket.receive_text()
        except:
            t_connections.remove(websocket)
    except:
        raise HTTPException(status_code=400, detail="WebSocket connection failed")

