import os
import math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from torch_geometric.nn import SAGEConv
from torch_geometric.utils import add_self_loops

from qiskit.primitives import Sampler
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit_machine_learning.neural_networks import SamplerQNN
from qiskit_machine_learning.connectors import TorchConnector

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_DIR = "final_models"
GNN_ENCODER_PATH = f"{MODEL_DIR}/gnn_encoder.pt"
NODE_EMB_PATH = f"{MODEL_DIR}/node_embeddings.npy"
QMODEL_PATH = f"{MODEL_DIR}/qmodel_final_3.pt"  # updated

N_QUBITS = 3  
REPS = 1

TOP_CATEGORIES = [
    "entertainment", "electronics", "fashion",
    "food", "grocery", "travel", "health", "other"
]
NUM_FEATURES = 5 + len(TOP_CATEGORIES)


def transaction_to_features(tx: dict):
    ts = pd.to_datetime(tx.get("timestamp", pd.Timestamp.now()))
    hour = ts.hour

    feat = [
        float(tx.get("amount", 0)),
        math.sin(2 * math.pi * hour / 24),
        math.cos(2 * math.pi * hour / 24),
        int(tx.get("is_high_risk_merchant", 0)),
        float(tx.get("location_distance_km", 0))
    ]

    cat = tx.get("merchant_category", "other")
    cat = cat if cat in TOP_CATEGORIES else "other"
    onehot = [1.0 if cat == c else 0.0 for c in TOP_CATEGORIES]

    return np.array(feat + onehot, dtype=np.float32)


class GNNEncoder(nn.Module):
    def __init__(self, in_dim, hidden=64, out_dim=16):
        super().__init__()
        self.conv1 = SAGEConv(in_dim, hidden)
        self.bn1 = nn.BatchNorm1d(hidden)
        self.conv2 = SAGEConv(hidden, out_dim)

    def forward(self, x, edge_index):
        # Ensure self-loops so GraphSAGE works even with single node
        edge_index, _ = add_self_loops(edge_index, num_nodes=x.size(0))
        x = self.conv1(x, edge_index)
        x = self.bn1(x)
        x = F.relu(x)
        return self.conv2(x, edge_index)


# Load GNN
gnn = GNNEncoder(NUM_FEATURES).to(DEVICE)
gnn.load_state_dict(torch.load(GNN_ENCODER_PATH, map_location=DEVICE))
gnn.eval()

# Load node embeddings and setup PCA + scaler
node_emb = np.load(NODE_EMB_PATH)
pca = PCA(n_components=N_QUBITS)
pca.fit(node_emb)

scaler = MinMaxScaler((0, math.pi))
scaler.fit(pca.transform(node_emb))

# Setup Quantum Circuit
feature_map = ZZFeatureMap(N_QUBITS, reps=REPS)
ansatz = RealAmplitudes(N_QUBITS, reps=REPS)
qc = feature_map.compose(ansatz)

qnn = SamplerQNN(
    sampler=Sampler(options={"shots": None}),
    circuit=qc,
    input_params=feature_map.parameters,
    weight_params=ansatz.parameters
)

torch_qnn = TorchConnector(qnn).to(DEVICE)


class QuantumClassifier(nn.Module):
    def __init__(self, qnn, out_dim):
        super().__init__()
        self.qnn = qnn
        self.mlp = nn.Sequential(
            nn.Linear(out_dim, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Linear(32, 2)
        )

    def forward(self, x):
        return self.mlp(self.qnn(x))


# Determine output dimension
with torch.no_grad():
    out_dim = torch_qnn(torch.zeros(1, N_QUBITS, dtype=torch.float32).to(DEVICE)).shape[1]

qmodel = QuantumClassifier(torch_qnn, out_dim).to(DEVICE)
qmodel.load_state_dict(torch.load(QMODEL_PATH, map_location=DEVICE))
qmodel.eval()


def predict_transaction(tx: dict):
    feat = transaction_to_features(tx)
    x = torch.tensor(feat, dtype=torch.float32).unsqueeze(0).to(DEVICE)

    # Use self-loops as minimal graph
    edge_index = torch.empty((2, 0), dtype=torch.long).to(DEVICE)

    with torch.no_grad():
        emb = gnn(x, edge_index).cpu().numpy()
        emb_pca = pca.transform(emb)
        emb_scaled = scaler.transform(emb_pca)
        logits = qmodel(torch.tensor(emb_scaled, dtype=torch.float32).to(DEVICE))
        prob = torch.softmax(logits, 1)[0, 1].item()

    return {
        "fraud_probability": prob,
        "is_fraud": bool(prob > 0.7),
        "risk_score": round(prob*100, 2)
    }
