import csv
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

client = AsyncIOMotorClient("mongodb+srv://322103310091_db_user:ZzDlytpXR8qQquDN@cluster0.xllkeno.mongodb.net/?appName=Cluster0")
db = client["quantum_fraud"]

BATCH_SIZE = 5000  

async def import_transactions():
    with open("./../datasets/transactions.csv") as f:
        reader = csv.DictReader(f)
        batch = []
        count = 0
        for row in reader:
            tx_doc = {
                "tx_id": row["tx_id"],
                "card_id": row["card_id"],
                "device_id": row["device_id"],
                "merchant_id": row["merchant_id"],
                "amount": float(row["amount"]),
                "timestamp": datetime.fromisoformat(row["timestamp"]),
                "merchant_category": row["merchant_category"],
                "is_high_risk_merchant": int(row["is_high_risk_merchant"]),
                "location_distance_km": float(row["location_distance_km"]),
                "label": int(row["label"]),
                "neighbors": [],
                "neighbor_edge_types": []
            }
            batch.append(tx_doc)
            count += 1

            if len(batch) >= BATCH_SIZE:
                await db["transactions"].insert_many(batch)
                batch = []

        # insert remaining
        if batch:
            await db["transactions"].insert_many(batch)

    print(f"✔ Imported {count} transactions")


async def import_edges():
    with open("./../datasets/edges.csv") as f:
        reader = csv.DictReader(f)
        operations = []
        count = 0
        for row in reader:
            operations.append(
                asyncio.ensure_future(
                    db["transactions"].update_one(
                        {"tx_id": row["source"]},
                        {"$push": {"neighbors": row["target"], "neighbor_edge_types": row["edge_type"]}}
                    )
                )
            )
            count += 1

            # execute in batches
            if len(operations) >= BATCH_SIZE:
                await asyncio.gather(*operations)
                operations = []

        if operations:
            await asyncio.gather(*operations)

    print(f"✔ Imported {count} edges")


async def main():
    await import_transactions()
    await import_edges()

asyncio.run(main())
