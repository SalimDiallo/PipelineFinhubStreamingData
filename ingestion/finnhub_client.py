"""
Client pour récupérer des données de marché depuis Finnhub.

- WebSocket : trades en temps réel (`wss://ws.finnhub.io`)
- REST      : candles OHLC (endpoint premium selon le plan)

Note : sur le plan gratuit Finnhub, seul le flux `trade` est diffusé par
WebSocket. Les quotes et candles temps réel nécessitent un plan payant.
"""

import json
from typing import Callable, Optional

import requests
import websocket  # fourni par le paquet `websocket-client`

from ingestion import config


class FinnhubClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.FINNHUB_API_KEY
        if not self.api_key:
            raise ValueError("API key Finnhub manquante")

        self.base_url = "https://finnhub.io/api/v1"
        self.ws_url = f"wss://ws.finnhub.io?token={self.api_key}"

    # -------------------------
    # 🔵 REST API (historique)
    # -------------------------

    def get_candles(self, symbol: str, resolution: str, start: int, end: int):
        """
        Récupère les données OHLC (candles).
        resolution: 1, 5, 15, 60, D, W, M
        """
        url = f"{self.base_url}/stock/candle"
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": start,
            "to": end,
            "token": self.api_key,
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Erreur API Finnhub: {response.text}")

        data = response.json()
        if data.get("s") != "ok":
            return None

        return {
            "symbol": symbol,
            "open": data["o"],
            "high": data["h"],
            "low": data["l"],
            "close": data["c"],
            "volume": data["v"],
            "timestamp": data["t"],
        }

    # -------------------------
    # 🟢 WebSocket (temps réel)
    # -------------------------

    def start_stream(
        self,
        symbols: list,
        on_message: Callable[[dict], None],
    ):
        """
        Ouvre le flux WebSocket et appelle `on_message(event)` pour chaque
        trade reçu. Chaque event est un dict normalisé :

            {
              "symbol": "AAPL",
              "price": 189.23,
              "volume": 100,
              "timestamp": 1710001234,
              "type": "trade"
            }

        `run_forever` est bloquant : la reconnexion automatique est gérée par
        `websocket-client` via `reconnect`.
        """

        def on_open(ws):
            print("🔌 Connexion WebSocket établie")
            for symbol in symbols:
                ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))
                print(f"   ➜ abonnement à {symbol}")

        def on_message_ws(ws, message):
            data = json.loads(message)

            # Finnhub envoie aussi des messages de type "ping" sans champ "data"
            if data.get("type") != "trade" or "data" not in data:
                return

            for item in data["data"]:
                on_message(
                    {
                        "symbol": item.get("s"),
                        "price": item.get("p"),
                        "volume": item.get("v"),
                        "timestamp": item.get("t"),
                        "type": "trade",
                    }
                )

        def on_error(ws, error):
            print(f"❌ Erreur WebSocket: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("🔌 Connexion fermée")

        ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message_ws,
            on_error=on_error,
            on_close=on_close,
        )

        # reconnect : délai (s) avant nouvelle tentative en cas de coupure
        ws.run_forever(reconnect=5)
