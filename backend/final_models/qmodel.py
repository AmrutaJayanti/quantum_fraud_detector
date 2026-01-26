# backend/final_models/qmodel_final_2.py
import torch
import torch.nn as nn
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit_machine_learning.neural_networks import SamplerQNN
from qiskit.primitives import Sampler
from qiskit_machine_learning.connectors import TorchConnector

class QuantumClassifier(nn.Module):
    def __init__(self, qnn_module: nn.Module, qnn_out_dim: int, mid_dim: int = 32):
        super().__init__()
        self.qnn = qnn_module
        self.mlp = nn.Sequential(
            nn.Linear(qnn_out_dim, mid_dim),
            nn.ReLU(),
            nn.BatchNorm1d(mid_dim),
            nn.Linear(mid_dim, 2)
        )

    def forward(self, x):
        qout = self.qnn(x)
        return self.mlp(qout)

def build_qnn(device="cpu", n_qubits=2, reps=1):
    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=reps)
    ansatz = RealAmplitudes(num_qubits=n_qubits, reps=reps)
    qc = feature_map.compose(ansatz)
    sampler = Sampler()
    qnn = SamplerQNN(
        sampler=sampler,
        circuit=qc,
        input_params=feature_map.parameters,
        weight_params=ansatz.parameters,
    )
    torch_qnn = TorchConnector(qnn).to(device)
    return torch_qnn
