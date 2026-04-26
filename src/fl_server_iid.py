from pathlib import Path
from typing import Dict, List

import flwr as fl
import numpy as np
import tensorflow as tf
import pandas as pd

from sklearn.metrics import confusion_matrix, classification_report

from fl_model import create_mlp


BASE_DIR = Path(__file__).resolve().parents[1]
PREP_DIR = BASE_DIR / "preprocessed"
TEST_PATH = PREP_DIR / "test.csv"


def load_test_data():
    df = pd.read_csv(TEST_PATH)
    X = df.drop(columns=["Label"]).values.astype("float32")
    y = df["Label"].values.astype("int64")
    print(f"[SERVER] Test data shape: X={X.shape}, y={y.shape}")
    return X, y


def get_evaluate_fn(model: tf.keras.Model):
    """
    Create centralized evaluation function for server-side evaluation.

    On each round, evaluate loss and accuracy on the global TEST set.
    On the final round (here assumed to be round 10), also print
    confusion matrix and classification report.
    """

    X_test, y_test = load_test_data()

    # Hard-coded label mapping used throughout the project
    class_names = ["DoS", "Normal", "Web"]

    def evaluate(server_round: int, parameters: List[np.ndarray], config: Dict):
        model.set_weights(parameters)
        loss, acc = model.evaluate(X_test, y_test, verbose=0)
        print(f"[SERVER] Round {server_round} - Test loss: {loss:.4f}, acc: {acc:.4f}")

        # Only print confusion matrix and classification report on final round
        # (change 10 if you change num_rounds)
        if server_round == 10:
            print("\n[SERVER] Final round reached – generating confusion matrix...")

            # Predict class probabilities and take argmax
            y_prob = model.predict(X_test, verbose=0)
            y_pred = np.argmax(y_prob, axis=1)

            cm = confusion_matrix(y_test, y_pred)
            print("\nConfusion Matrix (rows = true, cols = predicted):")
            print(cm)

            print("\nClassification Report:")
            print(classification_report(y_test, y_pred, target_names=class_names))

        return float(loss), {"accuracy": float(acc)}

    return evaluate


def fit_config(server_round: int):
    """Send training config to clients each round."""
    config = {
        "local_epochs": 1,
        "batch_size": 64,
    }
    print(f"[SERVER] Sending fit_config for round {server_round}: {config}")
    return config


def main():
    # Initialise a model on the server for evaluation
    input_dim = 76
    num_classes = 3
    model = create_mlp(input_dim=input_dim, num_classes=num_classes)

    # Define strategy
    strategy = fl.server.strategy.FedAvg(
        fraction_fit=1.0,
        fraction_evaluate=1.0,  # let all clients evaluate locally
        min_fit_clients=3,
        min_evaluate_clients=3,
        min_available_clients=3,
        on_fit_config_fn=fit_config,
        evaluate_fn=get_evaluate_fn(model),  # global test eval
    )

    # Start server
    print("[SERVER] Starting Flower server (FL experiment)...")
    fl.server.start_server(
        server_address="127.0.0.1:8080",
        config=fl.server.ServerConfig(num_rounds=10),
        strategy=strategy,
    )


if __name__ == "__main__":
    main()
