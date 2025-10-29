from fastapi import APIRouter, HTTPException, Request
from server.models.schemas import Order

router = APIRouter()

# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "ok"}

# Endpoint to place a new order
@router.post("/orders")
async def place_order(request: Request, order: Order):
    try:
        engine = request.app.state.engine
        trades = engine.process_order(order)
        return {"status": "order_placed", "trades": trades}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unstructured order data") from e
