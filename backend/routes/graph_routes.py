from fastapi import APIRouter, HTTPException
from crud.graph_crud import GraphStore

router = APIRouter(prefix="/graph")
store = GraphStore()

@router.get("/transaction/{tx_id}")
async def graph_by_transaction(tx_id: str):
    graph = await store.get_subgraph(tx_id)
    if not graph:
        raise HTTPException(404, "Transaction not found")
    return graph
