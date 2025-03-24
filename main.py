import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import pennylane as qml
import numpy as np

# 🧠 Set up quantum device
dev = qml.device("default.qubit", wires=2, shots=1000)
app = FastAPI()

# 🔐 Quantum encryption circuit
@qml.qnode(dev)
def qme_encrypt(message_bit):
    if message_bit == 1:
        qml.X(wires=0)
    qml.Hadamard(wires=1)
    qml.CNOT(wires=[1, 0])
    qml.RZ(0.2, wires=0)
    qml.RY(np.pi / 4, wires=1)
    return qml.sample(wires=[0, 1])

# 🧊 Schema
class EncryptRequest(BaseModel):
    bit: int

@app.get("/")
def root():
    return {"message": "Quantum API is live!"}

@app.get("/encrypt")
def encrypt(bit: int):
    sample = qme_encrypt(bit).tolist()
    return {
        "input_bit": bit,
        "encrypted_output": sample,
        "shots": len(sample),
        "description": "Quantum Mirror Encrypted Result"
    }

@app.get("/verify")
def verify(bit: int):
    from collections import Counter
    import math
    sample = qme_encrypt(bit).tolist()
    counts = Counter(tuple(x) for x in sample)
    total = sum(counts.values())
    probs = { ''.join(map(str, k)) : round(v / total, 4) for k, v in counts.items() }
    entropy = -sum(p * math.log2(p) for p in probs.values())
    return {
        "input_bit": bit,
        "output_distribution": probs,
        "entropy": round(entropy, 4),
        "interpretation": "Higher entropy = more uniform encryption. Bias = mirrored entanglement."
    }

# 🚀 Entry point for Render to launch FastAPI
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
