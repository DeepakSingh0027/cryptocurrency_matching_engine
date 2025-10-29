# Cryptocurrency Matching Engine

A high-performance **cryptocurrency matching engine** built with **Python** and **FastAPI**, supporting **REST** and **WebSocket APIs** for order management, trade matching, and market data broadcasting.

---

## Overview

This project implements a prototype matching engine that replicates the core functionalities of real-world cryptocurrency exchanges such as Binance or Coinbase.  
It handles order submission, matching (LIMIT, MARKET, IOC, FOK), and real-time data dissemination.

---

## System Architecture

```
+----------------------------------------------------------+
|                  Cryptocurrency Matching Engine          |
|----------------------------------------------------------|
| +----------------------+     +----------------------+    |
| |       engine/        |<--->|      models/         |    |
| |----------------------|     |----------------------|    |
| | MatchingEngine       |     | Pydantic Schemas     |    |
| | OrderBook (per pair) |     | (Order, Trade, etc.) |    |
| +----------------------+     +----------------------+    |
|       |                ^                                 |
|       v                |                                 |
| +----------------------+      +---------------------+    |
| |     api/             |<---->|      utils/         |    |
| |----------------------|      |---------------------|    |
| | FastAPI REST &       |      | Logging             |    |
| | WebSocket endpoints  |      | Market broadcasting |    |
| | (order, health, etc) |      +---------------------+    |
| +----------------------+                            ^    |
|           |                                         |    |
|           v                                         |    |
| +----------------------+                            |    |
| |      tests/          | <--------------------------+    |
| |----------------------|                                 |
| | Unit + integration   |                                 |
| | tests for engine,    |                                 |
| | orderbook, APIs      |                                 |
| +----------------------+                                 |
+----------------------------------------------------------+
```

---

## Project Structure

| Directory | Description                                                        |
| --------- | ------------------------------------------------------------------ |
| `engine/` | Core matching logic, order books, and price-time priority handling |
| `models/` | Pydantic schemas for data validation and structure                 |
| `api/`    | FastAPI routes for REST endpoints                                  |
| `utils/`  | Logging and real-time WebSocket broadcasting utilities             |
| `tests/`  | Unit and integration tests for validation                          |

---

## Key Features

- Implements **price-time priority** order matching.
- Supports order types: **LIMIT**, **MARKET**, **IOC**, and **FOK**.
- Real-time **WebSocket** updates for trades and market data.
- **REG NMS-inspired** BBO (Best Bid/Offer) dissemination logic.
- Clean modular structure for **scalability and testing**.

---

## API Endpoints

### REST Endpoints

| Method | Endpoint  | Description              |
| ------ | --------- | ------------------------ |
| `GET`  | `/health` | Health check for the API |
| `POST` | `/orders` | Submit a new order       |

### WebSocket Channels

| Channel      | Description                          |
| ------------ | ------------------------------------ |
| `/ws/market` | Real-time order book and BBO updates |
| `/ws/trades` | Live trade execution stream          |

---

## Matching Algorithm Overview

- **Order Matching:** Matches incoming orders against the opposite side (buy vs. sell) using price-time priority.
- **Partial Fills:** Supported — unfilled quantities are handled based on order type.
- **Data Structures:** Uses `SortedDict` for fast price lookups and `deque` for FIFO within price levels.
- **FOK Handling:** Ensures full liquidity before execution, else cancels.
- **Broadcasting:** Market data disseminated only when BBO changes.

---

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Data Structures:** sortedcontainers (SortedDict), deque
- **WebSocket:** Built-in FastAPI WebSocket support
- **Testing:** pytest

---

## Running Locally

```bash
# Clone repository
git clone https://github.com/DeepakSingh0027/cryptocurrency_matching_engine.git
cd cryptocurrency_matching_engine

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn server.main:app --reload

# Check Health
http://127.0.0.1:8000/appV1/health
```

---

## Example Order Payload

```json
{
  "symbol": "BTC-USDT",
  "side": "BUY",
  "type": "LIMIT",
  "price": 60000,
  "quantity": 0.5
}
```

---

## Tests

Run tests to ensure correctness of matching and broadcasting logic:

```bash
pytest -v
```

---

## Design Philosophy

The engine follows a **modular architecture** ensuring clear separation of logic:

- Each trading pair has an independent `OrderBook`.
- Matching follows deterministic, price-time order.
- Built for **educational and research purposes** — simple yet scalable.

---

## Author

**Deepak Singh Deopa**  
B.Tech CSE @ Graphic Era University  
Passionate about financial systems, scalability, and backend engineering.

---
