import uuid
from database import db

class TransactionStore:
    def __init__(self):
        self.collection = db.transactions
        self.edges = db.edges  # optional if you have separate edges collection

    async def get(self, tx_id: str):
        doc = await self.collection.find_one({"tx_id": tx_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def list(self, skip=0, limit=10):
        cursor = self.collection.find().skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def create(self, data: dict):
        if not data.get("tx_id"):
            data["tx_id"] = str(uuid.uuid4())

        # ----------------- GENERATE NEIGHBORS -----------------
        neighbors = []
        edge_types = []

        # Same card
        card_matches = self.collection.find({"card_id": data["card_id"]})
        async for tx in card_matches:
            if tx["tx_id"] != data["tx_id"]:
                neighbors.append(tx["tx_id"])
                edge_types.append("same_card")
                # Update neighbor to include this new tx
                await self.collection.update_one(
                    {"tx_id": tx["tx_id"]},
                    {"$push": {"neighbors": data["tx_id"], "neighbor_edge_types": "same_card"}}
                )

        # Same device
        device_matches = self.collection.find({"device_id": data["device_id"]})
        async for tx in device_matches:
            if tx["tx_id"] != data["tx_id"] and tx["tx_id"] not in neighbors:
                neighbors.append(tx["tx_id"])
                edge_types.append("same_device")
                await self.collection.update_one(
                    {"tx_id": tx["tx_id"]},
                    {"$push": {"neighbors": data["tx_id"], "neighbor_edge_types": "same_device"}}
                )

        # Same merchant
        merchant_matches = self.collection.find({"merchant_id": data["merchant_id"]})
        async for tx in merchant_matches:
            if tx["tx_id"] != data["tx_id"] and tx["tx_id"] not in neighbors:
                neighbors.append(tx["tx_id"])
                edge_types.append("same_merchant")
                await self.collection.update_one(
                    {"tx_id": tx["tx_id"]},
                    {"$push": {"neighbors": data["tx_id"], "neighbor_edge_types": "same_merchant"}}
                )

        # Save neighbors
        data["neighbors"] = neighbors
        data["neighbor_edge_types"] = edge_types

        # Insert the new transaction
        res = await self.collection.insert_one(data)
        data["_id"] = str(res.inserted_id)
        return data

    async def update(self, tx_id: str, patch: dict):
        await self.collection.update_one({"tx_id": tx_id}, {"$set": patch})
        return await self.get(tx_id)

    async def delete(self, tx_id: str):
        # Remove from neighbors of others
        await self.collection.update_many(
            {"neighbors": tx_id},
            {"$pull": {"neighbors": tx_id, "neighbor_edge_types": {"$exists": True}}}
        )

        res = await self.collection.delete_one({"tx_id": tx_id})
        return res.deleted_count > 0


def get_store():
    return TransactionStore()
