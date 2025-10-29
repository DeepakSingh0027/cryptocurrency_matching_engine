import logging
from sortedcontainers import SortedDict
from collections import deque
from decimal import Decimal
from server.models.schemas import Order, OrderSide, OrderType, Trade
import time, uuid
import uvicorn
import json

logger = logging.getLogger("uvicorn.error")

# Order Book Class
class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol                  # trading pair symbol
        self.bids = SortedDict(lambda x: -x)  # highest price first
        self.asks = SortedDict()              # lowest price first
        self.order_map = {}                   # order_id → (side, price)  
        self.last_bbo = None                  # for BBO change detection
        self.trades = []                      # store trade executions

    # Get trade history
    def get_trade_history(self):
        """Return list of executed trades."""
        return self.trades

    # Add orders to book
    def add_order_to_book(self, order: Order):
        """Add order to order book respecting price levels and FIFO order."""
        book = self.bids if order.side == OrderSide.BUY else self.asks
        if order.price not in book:
            book[order.price] = deque()
        book[order.price].append(order)
        self.order_map[order.order_id] = (order.side, order.price)
        return True

    # Remove orders from book
    def remove_order(self, order_id: str):
        """Remove order from book by ID."""
        if order_id not in self.order_map:
            return False
        # Retrieve side and price
        side, price = self.order_map.pop(order_id)
        # Determine book to remove from
        book = self.bids if side == OrderSide.BUY else self.asks
        # Get the queue at that price level
        queue = book.get(price)
        if queue:
            # Remove the order from the queue
            queue = deque(o for o in queue if o.order_id != order_id)
            if queue:
                book[price] = queue
            else:
                del book[price]
        return True

    # Find Best Bid and Offer
    def get_bbo(self):
        """Return best bid/ask snapshot."""
        # Find the best bid and ask prices
        best_bid = next(iter(self.bids.items()), (None, None))
        best_ask = next(iter(self.asks.items()), (None, None))
        # Construct BBO dictionary
        bbo = {
            "symbol": self.symbol,
            "best_bid": best_bid[0],
            "best_bid_qty": sum(o.quantity for o in best_bid[1]) if best_bid[1] else None,
            "best_ask": best_ask[0],
            "best_ask_qty": sum(o.quantity for o in best_ask[1]) if best_ask[1] else None,
        }
        return bbo

    # BBO Dissemination
    def maybe_disseminate_bbo(self):
        """Publish BBO only if changed."""
        new_bbo = self.get_bbo()
        # Check if BBO has changed
        if new_bbo != self.last_bbo:
            self.last_bbo = new_bbo
            logger.info(f"[BBO UPDATE] {new_bbo}")

    # Order Matching Logic
    def match_order(self, incoming: Order):
        """Handle order matching, price-time priority, and order types."""

        trades = []
        remaining_qty = incoming.quantity

        # Determine opposing book
        opposing_book = self.asks if incoming.side == OrderSide.BUY else self.bids

        # Matching function
        def is_match(price):
            if incoming.side == OrderSide.BUY:
                return price <= incoming.price if incoming.type != OrderType.MARKET else True
            else:
                return price >= incoming.price if incoming.type != OrderType.MARKET else True

        # FOK: Must execute fully immediately or cancel
        if incoming.type == OrderType.FOK:
            # find total available quantity at matching prices
            total_available = Decimal("0")
            total_available = sum(
                sum(o.quantity for o in q)
                for p, q in opposing_book.items()
                if is_match(p)
            )
            # If insufficient, cancel entire order
            if total_available < incoming.quantity:
                logger.info(f"[FOK CANCELLED] {incoming.order_id} - Insufficient liquidity.")
                return []
            else:
                # Execute fully (same logic as LIMIT but without resting)
                logger.info(f"[FOK EXECUTING] {incoming.order_id} - Full liquidity available.")
                # Create a temporary LIMIT order
                temp_order = Order(**{**incoming.dict(), "type": OrderType.LIMIT})
                trades = self.match_order(temp_order)
                self.maybe_disseminate_bbo()
                logger.info(f"[FOK FILLED] {incoming.order_id} - Executed {sum(t.quantity for t in trades)} units.")
                return trades

        # Iterate over opposing price levels
        matched_prices = []
        for price, orders in list(opposing_book.items()):
            if not is_match(price):
                break
            # Match orders at this price level
            while orders and remaining_qty > 0:
                resting = orders[0]
                trade_qty = min(remaining_qty, resting.quantity)

                # Record trade
                trade = Trade(
                    symbol=self.symbol,
                    price=price,
                    quantity=trade_qty,
                    maker_order_id=resting.order_id,
                    taker_order_id=incoming.order_id,
                    aggressor_side=incoming.side
                )
                trades.append(trade)
                self.trades.append(trade)

                # Update quantities
                resting.quantity -= trade_qty
                remaining_qty -= trade_qty

                if resting.quantity <= 0:
                    orders.popleft()
                    self.order_map.pop(resting.order_id, None)

                if remaining_qty <= 0:
                    break

            if not orders:
                matched_prices.append(price)
            if remaining_qty <= 0:
                break

        # Clean up empty price levels
        for price in matched_prices:
            opposing_book.pop(price, None)

        # Handle order types
        if incoming.type == OrderType.MARKET:
            # MARKET: no resting, cancel leftover
            remaining_qty = Decimal("0")

        elif incoming.type == OrderType.LIMIT:
            # LIMIT: rest leftover if any
            if remaining_qty > 0:
                incoming.quantity = remaining_qty
                self.add_order_to_book(incoming)

        elif incoming.type == OrderType.IOC:
            # IOC: cancel unfilled portion immediately
            remaining_qty = Decimal("0")

        # Disseminate BBO after any match
        self.maybe_disseminate_bbo()

        return trades

    # Public Order Processing

    def process_order(self, order: Order):
        """Public method to receive any new order event."""
        logger.info(f"Processing new order: {order.type} {order.side} {order.quantity}@{order.price}")
        trades = self.match_order(order)
        logger.info(f"All Trades Executed: {len(self.trades)}")
        return trades
