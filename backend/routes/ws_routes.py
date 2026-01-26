import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.ws_manager import manager
from services.predictor import predict_transaction  

router = APIRouter()

@router.websocket("/ws/transactions")
async def websocket_transactions(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()

            # keep-alive ping
            if data.lower() == "ping":
                await ws.send_json({"type": "pong"})
                continue

            tx = json.loads(data)

            result = predict_transaction(tx)

            message = {
                "type": "NEW_TRANSACTION",
                "data": {**tx, **result}
            }

            await manager.broadcast(message)

    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        print(f"WS error: {e}")
        manager.disconnect(ws)
