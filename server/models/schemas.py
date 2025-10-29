from pydantic import BaseModel, Field
from enum import Enum
from decimal import Decimal
import uuid, time

# Enums for order side and type
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

# Enums and models for orders and trades
class OrderType(str,Enum):
    MARKET = "market"
    LIMIT = "limit"
    IOC = "ioc"
    FOK = "fok"

# Model for orders
class Order(BaseModel):
    order_id : str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the order")
    symbol : str
    side: OrderSide
    type: OrderType
    price: Decimal|None = None
    quantity: Decimal
    timestamp: float = Field(default_factory=lambda:time.time())

# Model for trades
class Trade(BaseModel):
    trade_id : str = Field(default_factory = lambda:str(uuid.uuid4()))
    symbol : str
    price: Decimal
    quantity: Decimal
    maker_order_id: str
    taker_order_id: str
    aggressor_side: OrderSide
    timestamp: float = Field(default_factory=lambda:time.time())
