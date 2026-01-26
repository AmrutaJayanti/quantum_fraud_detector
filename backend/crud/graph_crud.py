from database import db

class GraphStore:
    def __init__(self):
        self.collection = db.transactions

    async def get_subgraph(self, tx_id: str):
        tx = await self.collection.find_one({"tx_id": tx_id})
        if not tx:
            return None

        nodes = {}
        edges = []

        # Central node
        nodes[tx["tx_id"]] = {
            "id": tx["tx_id"],
            "type": "transaction",
            "label": tx["tx_id"],
            "is_fraud": tx.get("label", 0)
        }

        neighbors = tx.get("neighbors", [])
        edge_types = tx.get("neighbor_edge_types", [])

        for nbr, etype in zip(neighbors, edge_types):
            nodes[nbr] = {
                "id": nbr,
                "type": "transaction",
                "label": nbr
            }
            edges.append({
                "from": tx["tx_id"],
                "to": nbr,
                "label": etype
            })

        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }

def get_store():
    return GraphStore()
