import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv

class GNNEncoder(nn.Module):
    def __init__(self, in_dim, hidden_dim=64, out_dim=16):
        super().__init__()
        self.conv1 = SAGEConv(in_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, out_dim)

    def forward(self, x, edge_index):
        if edge_index is None or edge_index.numel() == 0:
            return x  # fallback, no graph info
        h = self.conv1(x, edge_index)
        h = self.bn1(h)
        h = F.relu(h)
        h = self.conv2(h, edge_index)
        return h

class BaselineClassifier(nn.Module):
    def __init__(self, encoder, emb_dim=16, num_classes=2):
        super().__init__()
        self.encoder = encoder
        self.classifier = nn.Linear(emb_dim, num_classes)

    def forward(self, x, edge_index):
        emb = self.encoder(x, edge_index)
        return self.classifier(emb), emb
