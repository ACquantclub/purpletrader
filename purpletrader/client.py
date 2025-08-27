from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .errors import HTTPError
from .types import JsonDict, Order, Timeframe


@dataclass
class TradingEngineClient:
    base_url: str
    timeout: int = 30

    def _url(self, path: str) -> str:
        if self.base_url.endswith("/"):
            return f"{self.base_url[:-1]}{path}"
        return f"{self.base_url}{path}"

    def _handle_response(self, resp: requests.Response) -> JsonDict:
        if resp.status_code >= 400:
            body_text: Optional[str]
            try:
                body_text = resp.text
            except Exception:
                body_text = None
            message = None
            try:
                message = resp.json().get("error")
            except Exception:
                pass
            raise HTTPError(resp.status_code, message or resp.reason, body_text)
        try:
            return resp.json()
        except json.JSONDecodeError:
            return {"raw": resp.text}

    # Submit Order: POST /order
    def submit_order(self, order: Order | Dict[str, Any]) -> JsonDict:
        payload = order.to_payload() if isinstance(order, Order) else order
        resp = requests.post(self._url("/order"), json=payload, timeout=self.timeout)
        return self._handle_response(resp)

    # Get OrderBook: GET /api/v1/orderbook/{symbol}
    def get_orderbook(self, symbol: str) -> JsonDict:
        resp = requests.get(self._url(f"/api/v1/orderbook/{symbol}"), timeout=self.timeout)
        return self._handle_response(resp)

    # Get Trading Statistics: GET /api/v1/stats/{symbol}
    def get_stats(self, symbol: str) -> JsonDict:
        resp = requests.get(self._url(f"/api/v1/stats/{symbol}"), timeout=self.timeout)
        return self._handle_response(resp)

    # Get Statistics for Specific Timeframe: GET /api/v1/stats/{symbol}/{timeframe}
    def get_stats_timeframe(self, symbol: str, timeframe: Timeframe | str) -> JsonDict:
        tf = timeframe.value if isinstance(timeframe, Timeframe) else timeframe
        resp = requests.get(self._url(f"/api/v1/stats/{symbol}/{tf}"), timeout=self.timeout)
        return self._handle_response(resp)

    # Get All Statistics: GET /api/v1/stats/all
    def get_all_stats(self) -> JsonDict:
        resp = requests.get(self._url("/api/v1/stats/all"), timeout=self.timeout)
        return self._handle_response(resp)

    # Get Statistics Summary: GET /api/v1/stats/summary
    def get_stats_summary(self) -> JsonDict:
        resp = requests.get(self._url("/api/v1/stats/summary"), timeout=self.timeout)
        return self._handle_response(resp)

    # Get Leaderboard: GET /api/v1/leaderboard
    def get_leaderboard(self) -> JsonDict:
        resp = requests.get(self._url("/api/v1/leaderboard"), timeout=self.timeout)
        return self._handle_response(resp)

    # Health Check: GET /health
    def health(self) -> JsonDict:
        resp = requests.get(self._url("/health"), timeout=self.timeout)
        return self._handle_response(resp)

    # Admin endpoints

    # Admin Status: GET /admin/status with auth
    def admin_status(self, password: str, method: str = "query") -> JsonDict:
        if method == "query":
            resp = requests.get(self._url(f"/admin/status?password={password}"), timeout=self.timeout)
        elif method == "bearer":
            resp = requests.get(self._url("/admin/status"), headers={"Authorization": f"Bearer {password}"}, timeout=self.timeout)
        elif method == "header":
            resp = requests.get(self._url("/admin/status"), headers={"X-Admin-Password": password}, timeout=self.timeout)
        else:
            raise ValueError("method must be 'query', 'bearer', or 'header'")
        return self._handle_response(resp)

    # Stop Trading: POST /admin/stop_trading with auth
    def admin_stop_trading(self, password: str, method: str = "bearer") -> JsonDict:
        if method == "bearer":
            headers = {"Authorization": f"Bearer {password}"}
        elif method == "header":
            headers = {"X-Admin-Password": password}
        elif method == "query":
            resp = requests.post(self._url(f"/admin/stop_trading?password={password}"), timeout=self.timeout)
            return self._handle_response(resp)
        else:
            raise ValueError("method must be 'bearer', 'header', or 'query'")
        resp = requests.post(self._url("/admin/stop_trading"), headers=headers, timeout=self.timeout)
        return self._handle_response(resp)

    # Resume Trading: POST /admin/resume_trading with auth
    def admin_resume_trading(self, password: str, method: str = "bearer") -> JsonDict:
        if method == "bearer":
            headers = {"Authorization": f"Bearer {password}"}
        elif method == "header":
            headers = {"X-Admin-Password": password}
        elif method == "query":
            resp = requests.post(self._url(f"/admin/resume_trading?password={password}"), timeout=self.timeout)
            return self._handle_response(resp)
        else:
            raise ValueError("method must be 'bearer', 'header', or 'query'")
        resp = requests.post(self._url("/admin/resume_trading"), headers=headers, timeout=self.timeout)
        return self._handle_response(resp)

    # Flush System: POST /admin/flush_system with auth
    def admin_flush_system(self, password: str, method: str = "bearer") -> JsonDict:
        if method == "bearer":
            headers = {"Authorization": f"Bearer {password}"}
        elif method == "header":
            headers = {"X-Admin-Password": password}
        elif method == "query":
            resp = requests.post(self._url(f"/admin/flush_system?password={password}"), timeout=self.timeout)
            return self._handle_response(resp)
        else:
            raise ValueError("method must be 'bearer', 'header', or 'query'")
        resp = requests.post(self._url("/admin/flush_system"), headers=headers, timeout=self.timeout)
        return self._handle_response(resp)


