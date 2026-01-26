import { useEffect } from "react";

export default function useRealtimeTransactions(onMessage) {
  useEffect(() => {
    if (!onMessage) return;

    const ws = new WebSocket("ws://localhost:8000/ws/transactions");

    const keepAlive = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 30000);

    ws.onopen = () => console.log("WS connected");
    
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if(msg.type==="pong") return;
        onMessage(msg); // Use the correct callback
      } catch (err) {
        console.error("WS parse error:", err);
      }
    };

    ws.onclose = () => console.log("WS closed");
    ws.onerror = (err) => console.error("WS error:", err);

    return () => {
      clearInterval(keepAlive);
      ws.close();
    };
  }, [onMessage]);
}
