from datetime import datetime
import asyncio
import json


async def broadcast_market_update(app, engine):
    """Broadcast the latest market data update to all connected WebSocket clients for a given symbol."""
    connections = app.state.connections
    # Check if there are any WebSocket connections
    if connections is None:
        return
    # Get the latest order books from the engine
    orders = engine.get_orderbooks()
    # If there are no orders, return early
    if not orders:
        return 
    
    # Prepare the data to be broadcasted
    data = []
    for symbol, orderbook in orders.items():
        bbo = orderbook.get_bbo()
        data.append({
            "bbo": {
                "symbol": bbo["symbol"],
                "best_bid": str(bbo["best_bid"]),
                "best_bid_qty": str(bbo["best_bid_qty"]),
                "best_ask": str(bbo["best_ask"]),
                "best_ask_qty": str(bbo["best_ask_qty"]),
            },
            "order_book": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "symbol": symbol,
                "ask": [
                    [str(price), str(sum(o.quantity for o in order))]
                    for price, order in sorted(orderbook.asks.items())[:20]
                ],
                "bid": [
                    [str(price), str(sum(o.quantity for o in order))]
                    for price, order in sorted(orderbook.bids.items(), reverse=True)[:20]
                ]
            }
        })
    

    message = json.dumps(data)
    # Broadcast the message to all connected WebSocket clients
    for ws in connections:
        try:
            await ws.send_text(message)
        except:
            connections.remove(ws)


async def broadcast_trade_update(app, trades):
    """Broadcast the latest trade updates to all connected trade WebSocket clients."""
    # Check if there are any trade WebSocket connections
    t_connections = app.state.t_connections
    if t_connections is None:
        return

    # Prepare the trade data to be broadcasted
    data = []
    for trade in trades:
        data.append({
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "price": str(trade.price),
            "quantity": str(trade.quantity),
            "timestamp": trade.timestamp,
            "aggressor_side": trade.aggressor_side,
            "maker_order_id": trade.maker_order_id,
            "taker_order_id": trade.taker_order_id
        })

    message = json.dumps(data)
    # Broadcast the message to all connected trade WebSocket clients
    for ws in t_connections:
        try:
            await ws.send_text(message)
        except:
            t_connections.remove(ws)