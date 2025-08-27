# purpletrader

A lightweight Python client for the Live Trading Engine HTTP API.

## Installation

```bash
pip install .
```

## Usage

```python
from purpletrader import TradingEngineClient, Order, Timeframe

client = TradingEngineClient(base_url="http://localhost:8080")

# Submit order
resp = client.submit_order(Order(
    id="order_001",
    userId="trader_123",
    symbol="AAPL",
    type="LIMIT",
    side="BUY",
    quantity=100,
    price=150.25,
))
print(resp)

# Fetch data
print(client.get_orderbook("AAPL"))
print(client.get_stats("AAPL"))
print(client.get_stats_timeframe("AAPL", Timeframe.ONE_MINUTE))
print(client.get_all_stats())
print(client.get_stats_summary())
print(client.get_leaderboard())
print(client.health())

# Admin
password = "your_admin_password"
print(client.admin_status(password, method="query"))
print(client.admin_stop_trading(password, method="bearer"))
print(client.admin_resume_trading(password, method="header"))
print(client.admin_flush_system(password, method="header"))
```

## Notes
- Raises `HTTPError` on non-2xx responses with `status_code`, `message`, and `body`.
- Default timeout is 30s; override via `TradingEngineClient(timeout=...)`.
