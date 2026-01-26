from pydantic import BaseModel
from typing import Optional

class Transaction(BaseModel):
    tx_id: Optional[str] = None
    card_id: str
    device_id: str
    merchant_id: str
    amount: float
    timestamp: str
    merchant_category: str
    is_high_risk_merchant: int = 0
    location_distance_km: float
    fraud_probability: Optional[float] = 0.0
    label: int  
    is_fraud: Optional[bool]=False
    risk_score: Optional[float] = 0.0