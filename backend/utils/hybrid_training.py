import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import f1_score
from imblearn.over_sampling import SMOTE

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv

# ---------------------------
# 1️⃣ Load CSVs
# ---------------------------
tx_df = pd.read_csv("./datasets/transactions.csv")
edges_df = pd.read_csv("./datasets/edges.csv")

# ---------------------------
# 2️⃣ Build edge_index
# ---------------------------
tx_ids = tx_df['tx_id'].tolist()
id_to_idx = {tx: i for i, tx in enumerate(tx_ids)}

edge_list = []
for _, r in edges_df.iterrows():
    s, t = r['source'], r['target']
    if s in id_to_idx and t in id_to_idx:
        edge_list.append([id_to_idx[s], id_to_idx[t]])
        edge_list.append([id_to_idx[t], id_to_idx[s]])  # undirected

edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()

# ---------------------------
# 3️⃣ Feature engineering
# ---------------------------
df = tx_df.copy()
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
df['location_distance_km'] = pd.to_numeric(df.get('location_distance_km', 0.0), errors='coerce').fillna(0.0)
df['is_high_risk_merchant'] = pd.to_numeric(df.get('is_high_risk_merchant', 0), errors='coerce').fillna(0).astype(int)

top_categories = df['merchant_category'].value_counts().nlargest(8).index.tolist()
df['merchant_cat_reduced'] = df['merchant_category'].apply(lambda x: x if x in top_categories else 'other')
cat_dummies = pd.get_dummies(df['merchant_cat_reduced'], prefix='mcat').astype(np.float32)

feature_cols = ['amount', 'hour_sin', 'hour_cos', 'is_high_risk_merchant', 'location_distance_km']
feat_df = pd.concat([df[feature_cols].reset_index(drop=True), cat_dummies.reset_index(drop=True)], axis=1)
scaler = StandardScaler()
feat_df[feature_cols] = scaler.fit_transform(feat_df[feature_cols])
feat_df = feat_df.apply(pd.to_numeric, errors='coerce').fillna(0.0)

labels = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int).values

# ---------------------------
# 4️⃣ Train/Val/Test split
# ---------------------------
n_nodes = len(df)
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(sss.split(np.zeros(n_nodes), labels))
sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=1)
train_idx, val_idx = next(sss2.split(np.zeros(len(train_idx)), labels[train_idx]))

# ---------------------------
# 5️⃣ Handle class imbalance with SMOTE
# ---------------------------
sm = SMOTE(random_state=42)
X_train_smote, y_train_smote = sm.fit_resample(feat_df.iloc[train_idx].values.astype(np.float64), labels[train_idx])

# ---------------------------
# 6️⃣ Convert to torch tensors
# ---------------------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
X_all = torch.tensor(feat_df.values.astype(np.float32), dtype=torch.float32).to(device)
y_all = torch.tensor(labels, dtype=torch.long).to(device)
X_train_smote = torch.tensor(X_train_smote.astype(np.float32), dtype=torch.float32).to(device)
y_train_smote = torch.tensor(y_train_smote, dtype=torch.long).to(device)
train_idx_smote = torch.arange(len(X_train_smote), dtype=torch.long)
val_idx = torch.tensor(val_idx, dtype=torch.long)
test_idx = torch.tensor(test_idx, dtype=torch.long)

# ---------------------------
# 7️⃣ PyG Data
# ---------------------------
data = Data(x=X_all, edge_index=edge_index, y=y_all)

# ---------------------------
# 8️⃣ Define GNN
# ---------------------------
class GNNEncoder(nn.Module):
    def __init__(self, in_dim, hidden_dim=64, out_dim=16):
        super().__init__()
        self.conv1 = SAGEConv(in_dim, hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, out_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        return x

class BaselineClassifier(nn.Module):
    def __init__(self, encoder, emb_dim, num_classes=2):
        super().__init__()
        self.encoder = encoder
        self.classifier = nn.Linear(emb_dim, num_classes)

    def forward(self, x, edge_index):
        emb = self.encoder(x, edge_index)
        return self.classifier(emb), emb

encoder = GNNEncoder(in_dim=data.num_node_features, hidden_dim=64, out_dim=16).to(device)
model_baseline = BaselineClassifier(encoder, emb_dim=16, num_classes=2).to(device)
opt = Adam(model_baseline.parameters(), lr=1e-3, weight_decay=1e-5)
loss_fn = nn.CrossEntropyLoss()

# --------------------------- 9️⃣ Training loop ---------------------------
def eval_model(model, idx):
    model.eval()
    with torch.no_grad():
        logits, _ = model(X_all, edge_index)
        preds = logits.argmax(dim=1)
        return preds[idx]

from sklearn.metrics import classification_report, roc_auc_score

epochs = 40
best_val_f1 = 0.0
for epoch in range(1, epochs + 1):
    model_baseline.train()
    opt.zero_grad()
    logits, _ = model_baseline(X_train_smote, edge_index)
    loss = loss_fn(logits[train_idx_smote], y_train_smote)
    loss.backward()
    opt.step()

    val_preds = eval_model(model_baseline, val_idx)
    val_y = y_all[val_idx]
    acc = (val_preds == val_y).float().mean().item()
    f1 = f1_score(val_y.cpu().numpy(), val_preds.cpu().numpy(), zero_division=0)

    if f1 > best_val_f1:
        best_val_f1 = f1
        torch.save(model_baseline.state_dict(), "final_models/gnn_best_model.pt")
    
    if epoch % 5 == 0 or epoch == 1:
        print(f"Epoch {epoch} | loss={loss.item():.4f} val_acc={acc:.4f} val_f1={f1:.4f}")

# --------------------------- 10️⃣ Evaluate on Test ---------------------------
model_baseline.eval()
with torch.no_grad():
    test_preds = eval_model(model_baseline, test_idx)
    test_y = y_all[test_idx]
    test_acc = (test_preds == test_y).float().mean().item()
    test_f1 = f1_score(test_y.cpu().numpy(), test_preds.cpu().numpy(), zero_division=0)
    test_auc = roc_auc_score(test_y.cpu().numpy(), F.softmax(model_baseline(X_all, edge_index)[0][test_idx], dim=1)[:,1].cpu().numpy())
    
    print("\n===== TEST RESULTS =====")
    print(f"Test accuracy: {test_acc:.4f}")
    print(f"Test F1:       {test_f1:.4f}")
    print(f"Test AUC:      {test_auc:.4f}")
    print("\nClassification report:")
    print(classification_report(test_y.cpu().numpy(), test_preds.cpu().numpy(), digits=4))

# --------------------------- 11️⃣ Save embeddings + model weights ---------------------------
_, emb = model_baseline(X_all, edge_index)
embeddings = emb.detach().cpu().numpy()

os.makedirs("final_models", exist_ok=True)

torch.save(encoder.state_dict(), "final_models/gnn_encoder.pt")
torch.save(model_baseline.state_dict(), "final_models/baseline_model_weights.pt")
np.save("node_embeddings.npy", embeddings)
np.save("node_labels.npy", y_all.cpu().numpy())

print("✅ Saved GNN encoder weights, BaselineClassifier weights, node embeddings, and labels")
