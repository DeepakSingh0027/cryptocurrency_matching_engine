from server.models.schemas import Order, OrderSide, OrderType
from server.engine.orderbook import OrderBook
from server.utils.brodcast import broadcast_market_update, broadcast_trade_update
from decimal import Decimal
import time
import logging
import uvicorn
import asyncio

logger = logging.getLogger("uvicorn.error")

# Matching Engine
class MatchingEngine:
    def __init__(self, app=None):
        # FastAPI app for broadcasting updates
        self.app = app
        # Dictionary of symbol → OrderBook
        self.order_books = {}

    # Get or create order book for a symbol
    def get_orderbook(self, symbol: str):
        if symbol not in self.order_books:
            self.order_books[symbol] = OrderBook(symbol)
        return self.order_books[symbol]

    # Get all order books
    def get_orderbooks(self):
        return self.order_books

    # Process incoming order
    def process_order(self, order: Order):
        """Main entry point for handling any incoming order."""
        orderbook = self.get_orderbook(order.symbol)

        logger.info(f"[ENGINE] Processing Order: {order.side} {order.type} {order.quantity}@{order.price or 'MKT'}")

        # Pass order into orderbook for matching
        trades = orderbook.process_order(order)

        # After processing, broadcast market data update if app is available
        if self.app:
            asyncio.create_task(broadcast_market_update(self.app,self))

        # Broadcast trade updates if there are trades executed
        if trades:
            asyncio.create_task(broadcast_trade_update(self.app,trades))
            logger.info(f"[ENGINE] Executed {len(trades)} trade(s):")
            for t in trades:
                logger.info(f"Trade {t.trade_id} | {t.quantity}@{t.price} ({t.aggressor_side})")
        else:
            logger.info("[ENGINE] No trades executed")

        return trades
    
    # Get current Best Bid and Offer for a symbol
    def get_bbo(self, symbol: str):
        """Get current Best Bid and Offer for a symbol."""
        orderbook = self.get_orderbook(symbol)
        return orderbook.get_bbo()
