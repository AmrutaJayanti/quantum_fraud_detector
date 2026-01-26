from fastapi import APIRouter, HTTPException
from models.transaction import Transaction
from crud.transaction_crud import get_store
from services.predictor import predict_transaction
from services.ws_manager import manager  

router = APIRouter(prefix="/transactions")
store = get_store()

@router.post("")
async def create_transaction(tx: Transaction):
    pred = predict_transaction(tx.model_dump())

    tx.fraud_probability = pred["fraud_probability"]
    tx.risk_score = pred["risk_score"]
    tx.is_fraud = pred["is_fraud"]

    created = await store.create(tx.model_dump())

    await manager.broadcast({
        "type": "NEW_TRANSACTION",
        "data": created
    })

    return tx.model_dump()


@router.get("")
async def list_transactions(skip: int = 0, limit: int = 10):
    
    return await store.list(skip, limit)


@router.get("/{tx_id}")
async def get_transaction(tx_id: str):
    tx = await store.get(tx_id)
    if not tx:
        raise HTTPException(404, "Transaction not found")
    return tx


@router.put("/{tx_id}")
async def update_transaction(tx_id: str, tx: Transaction):
    updated = await store.update(
        tx_id,
        tx.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(404, "Transaction not found")
    return updated


# ---------------- DELETE ----------------
@router.delete("/{tx_id}")
async def delete_transaction(tx_id: str):
    ok = await store.delete(tx_id)
    if not ok:
        raise HTTPException(404, "Transaction not found")
    return {"deleted": True}
