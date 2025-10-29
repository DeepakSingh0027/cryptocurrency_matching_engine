from server.engine.matcher import MatchingEngine
from server.models.schemas import Order, OrderSide, OrderType
from decimal import Decimal


def test_basic_match():
    engine = MatchingEngine()

    # 1️ Add initial BUY at 62000 (should become best bid)
    buy = Order(symbol="BTC-USDT", side=OrderSide.BUY, type=OrderType.LIMIT,
                price=Decimal("62000"), quantity=Decimal("1"))
    engine.process_order(buy)
    bbo1 = engine.get_bbo("BTC-USDT")
    assert bbo1["best_bid"] == Decimal("62000")
    assert bbo1["best_ask"] is None  # no sellers yet

    # 2️ Add SELL at 61900 (should match immediately)
    sell = Order(symbol="BTC-USDT", side=OrderSide.SELL, type=OrderType.LIMIT,
                 price=Decimal("61900"), quantity=Decimal("2"))
    trades = engine.process_order(sell)
    bbo2 = engine.get_bbo("BTC-USDT")

    # One trade executed at resting BUY price 62000
    assert len(trades) == 1
    assert trades[0].price == Decimal("62000")
    assert trades[0].quantity == Decimal("1")

    # 1 BTC remaining on sell side @ 61900
    assert bbo2["best_bid"] is None
    assert bbo2["best_ask"] == Decimal("61900")

    # 3 Add new SELL at 62000 (higher than 61900 → no match)
    new_sell = Order(symbol="BTC-USDT", side=OrderSide.SELL, type=OrderType.LIMIT,
                     price=Decimal("62000"), quantity=Decimal("2"))
    engine.process_order(new_sell)
    bbo3 = engine.get_bbo("BTC-USDT")
    assert bbo3["best_ask"] == Decimal("61900")  # still the best ask

    # 4️ Add new BUY at 61900 (should match with existing SELL at 61900)
    new_buy = Order(symbol="BTC-USDT", side=OrderSide.BUY, type=OrderType.LIMIT,
                price=Decimal("61900"), quantity=Decimal("2"))
    trades = engine.process_order(new_buy)
    bbo4 = engine.get_bbo("BTC-USDT")

    # One trade executed at 61900
    assert len(trades) == 1
    assert trades[0].price == Decimal("61900")

    # Partial match → remaining BUY at 61900 and existing SELL at 62000
    assert bbo4["best_bid"] == Decimal("61900")
    assert bbo4["best_ask"] == Decimal("62000")

    print("✅ Final BBO:", bbo4)
