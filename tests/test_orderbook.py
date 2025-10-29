from server.engine.orderbook import OrderBook
from server.models.schemas import Order, OrderSide, OrderType
from decimal import Decimal

def test_bbo_updates():
    book = OrderBook(symbol="BTC-USDT")
    o1 = Order(symbol="BTC-USDT", side=OrderSide.BUY, type=OrderType.LIMIT, price=Decimal("62000"), quantity=Decimal("1"))
    o2 = Order(symbol="BTC-USDT", side=OrderSide.SELL, type=OrderType.LIMIT, price=Decimal("62500"), quantity=Decimal("1"))
    book.process_order(o1)
    book.process_order(o2)
    bbo = book.get_bbo()
    print("*******************************")
    print(bbo)
    print("*******************************")
    assert bbo["best_bid"] == Decimal("62000")
    assert bbo["best_ask"] == Decimal("62500")
