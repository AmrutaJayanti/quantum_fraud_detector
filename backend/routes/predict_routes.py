from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import pandas as pd

from models.transaction import Transaction
from services.predictor import predict_transaction

router = APIRouter(prefix="/predict", tags=["Predict"])

# ---------------- Single Transaction Prediction ----------------
@router.post("/single")
async def predict_single(tx: Transaction):
    try:
        pred = predict_transaction(tx.dict())
        return {
            "tx_id": tx.tx_id,
            "fraud_probability": pred["fraud_probability"],
            "label": 1 if pred["fraud_probability"] > 0.5 else 0 ,
            "risk_score": pred["risk_score"],
            "is_fraud": pred["is_fraud"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- Batch Prediction (CSV) ----------------
@router.post("/batch")
async def predict_batch(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")

    results = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()

        # Ensure proper types
        row_dict["amount"] = float(row_dict.get("amount", 0))
        row_dict["is_high_risk_merchant"] = int(row_dict.get("is_high_risk_merchant", 0))
        row_dict["location_distance_km"] = float(row_dict.get("location_distance_km", 0))

        # Run prediction
        pred = predict_transaction(row_dict)

        # Add label if exists (optional)
        label = int(row_dict.get("label", 0))

        results.append({
            "tx_id": row_dict.get("tx_id"),
            "card_id": row_dict.get("card_id"),
            "device_id": row_dict.get("device_id"),
            "merchant_id": row_dict.get("merchant_id"),
            "amount": row_dict.get("amount"),
            "timestamp": row_dict.get("timestamp"),
            "merchant_category": row_dict.get("merchant_category"),
            "is_high_risk_merchant": row_dict.get("is_high_risk_merchant"),
            "location_distance_km": row_dict.get("location_distance_km"),
            "label": label,  # actual label if present
            "is_fraud": pred["is_fraud"],  # predicted
            "fraud_probability": pred["fraud_probability"],
            "risk_score": pred["risk_score"]
        })

    return results