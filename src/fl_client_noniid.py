import argparse
from pathlib import Path
from typing import Tuple

import flwr as fl
import numpy as np
import pandas as pd
import tensorflow as tf

from fl_model import create_mlp


BASE_DIR = Path(__file__).resolve().parents[1]
PREP_DIR = BASE_DIR / "preprocessed"


def load_client_data(client_id: int) -> Tuple[np.ndarray, np.ndarray]:
    """Load Non-IID client data from preprocessed/noniid_client{client_id}.csv."""
    csv_path = PREP_DIR / f"noniid_client{client_id}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Client CSV not found: {csv_path}")

    print(f"[NONIID CLIENT {client_id}] Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)

    if "Label" not in df.columns:
        raise ValueError(f"[NONIID CLIENT {client_id}] 'Label' column missing in {csv_path}")

    X = df.drop(columns=["Label"]).values.astype("float32")
    y = df["Label"].values.astype("int64")

    print(f"[NONIID CLIENT {client_id}] Data shape: X={X.shape}, y={y.shape}")
    print(f"[NONIID CLIENT {client_id}] Class distribution:", np.bincount(y))
    return X, y


def train_val_split(
    X: np.ndarray, y: np.ndarray, val_ratio: float = 0.2, seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Simple local train/validation split (no stratification here due to Non-IID)."""
    rng = np.random.default_rng(seed)
    idx = np.arange(len(X))
    rng.shuffle(idx)

    split = int(len(X) * (1.0 - val_ratio))
    train_idx, val_idx = idx[:split], idx[split:]

    return X[train_idx], y[train_idx], X[val_idx], y[val_idx]


class NonIIDClient(fl.client.NumPyClient):
    def __init__(
        self,
        cid: int,
        model: tf.keras.Model,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
    ):
        self.cid = cid
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val

    def get_parameters(self, config):
        print(f"[NONIID CLIENT {self.cid}] get_parameters")
        return self.model.get_weights()

    def fit(self, parameters, config):
        print(f"[NONIID CLIENT {self.cid}] fit, config={config}")
        self.model.set_weights(parameters)

        epochs = int(config.get("local_epochs", 1))
        batch_size = int(config.get("batch_size", 64))

        self.model.fit(
            self.X_train,
            self.y_train,
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
        )

        return self.model.get_weights(), len(self.X_train), {}

    def evaluate(self, parameters, config):
        print(f"[NONIID CLIENT {self.cid}] evaluate")
        self.model.set_weights(parameters)
        loss, acc = self.model.evaluate(
            self.X_val,
            self.y_val,
            verbose=0,
        )
        return float(loss), len(self.X_val), {"accuracy": float(acc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cid",
        type=int,
        required=True,
        help="Client ID (1, 2, or 3 for Non-IID setup)",
    )
    parser.add_argument(
        "--server",
        type=str,
        default="127.0.0.1:8080",
        help="Flower server address",
    )
    args = parser.parse_args()

    # Load local Non-IID data
    X, y = load_client_data(args.cid)
    X_train, y_train, X_val, y_val = train_val_split(X, y, val_ratio=0.2)

    # Build local model
    input_dim = X_train.shape[1]
    num_classes = 3
    model = create_mlp(input_dim=input_dim, num_classes=num_classes)

    client = NonIIDClient(
        cid=args.cid,
        model=model,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
    )

    print(f"[NONIID CLIENT {args.cid}] Starting Flower NumPyClient...")
    fl.client.start_numpy_client(
        server_address=args.server,
        client=client,
    )


if __name__ == "__main__":
    main()
