from fastapi import FastAPI, Query
from pydantic import BaseModel
from collections import Counter
import math
import threading
import uvicorn
import numpy as np
import pennylane as qml

# Setup quantum device
dev = qml.device("default.qubit", wires=2, shots=1000)

app = FastAPI()

@qml.qnode(dev)
def qme_encrypt(message_bit):
    if message_bit == 1:
        qml.X(wires=0)
    qml.Hadamard(wires=1)
    qml.CNOT(wires=[1, 0])
    qml.RZ(0.2, wires=0)
    qml.RY(np.pi / 4, wires=1)
    return qml.sample(wires=[0, 1])

@app.get("/encrypt")
def encrypt(bit: int = Query(..., ge=0, le=1)):
    sample = qme_encrypt(bit).tolist()
    return {
        "input_bit": bit,
        "encrypted_output": sample,
        "shots": len(sample),
        "description": "Quantum Mirror Encrypted Result"
    }

@app.get("/verify")
def verify(bit: int = Query(..., ge=0, le=1)):
    sample = qme_encrypt(bit).tolist()
    counts = Counter(tuple(x) for x in sample)
    total = sum(counts.values())
    probs = { ''.join(map(str, k)) : round(v / total, 4) for k, v in counts.items() }
    entropy = -sum(p * math.log2(p) for p in probs.values())
    return {
        "input_bit": bit,
        "output_distribution": probs,
        "entropy": round(entropy, 4),
        "interpretation": "Higher entropy indicates more uniform encryption. Entangled bias shows mirrored influence."
    }
