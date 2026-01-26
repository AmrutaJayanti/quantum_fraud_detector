import asyncio
import random
from datetime import datetime
import websockets
import uuid
import json

API_WS_URL = "ws://localhost:8000/ws/transactions"
INTERVAL_SEC = 5

MERCHANT_CATEGORIES = [
    "entertainment", "electronics", "fashion",
    "food", "grocery", "travel", "health", "other"
]

async def run_simulator():
    async with websockets.connect(API_WS_URL) as ws:
        print("Simulator WS connected")
        while True:
            tx = {
                "tx_id": str(uuid.uuid4()),
                "card_id": "card_" + str(random.randint(1000, 9999)),
                "device_id": "dev_" + str(random.randint(100, 9999)),
                "merchant_id": "m_" + str(random.randint(1, 1000)),
                "amount": round(random.uniform(1, 500), 2),
                "timestamp": datetime.now().isoformat(),
                "merchant_category": random.choice(MERCHANT_CATEGORIES),
                "is_high_risk_merchant": random.choice([0, 1]),
                "location_distance_km": round(random.uniform(0, 20), 2),
                "label": 0
            }

            try:
                await ws.send(json.dumps(tx))
            except Exception as e:
                print("WS send error:", e)

            await asyncio.sleep(INTERVAL_SEC)

if __name__ == "__main__":
    asyncio.run(run_simulator())
