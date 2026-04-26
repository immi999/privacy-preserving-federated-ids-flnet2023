

# System Architecture

## 1. Overview

This project uses a Federated Learning architecture to build a privacy-preserving Intrusion Detection System.

The system follows a client-server design where multiple clients train a shared machine learning model without sending their raw network traffic data to the central server.

Each client keeps its own local dataset, trains the model locally, and sends only model weight updates to the server. The server then combines these updates using Federated Averaging to create an improved global IDS model.

---

## 2. High-Level Architecture

```text
                  ┌──────────────────────────┐
                  │      Flower Server       │
                  │                          │
                  │  - Sends global model    │
                  │  - Receives updates      │
                  │  - Applies FedAvg        │
                  │  - Evaluates model       │
                  └─────────────▲────────────┘
                                │
              Model Updates     │     Global Model Weights
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   Client 1    │       │   Client 2    │       │   Client 3    │
│               │       │               │       │               │
│ Local Dataset │       │ Local Dataset │       │ Local Dataset │
│ Local Training│       │ Local Training│       │ Local Training│
└───────────────┘       └───────────────┘       └───────────────┘
````

---

## 3. Main Components

The architecture contains four main components:

1. Dataset layer
2. Preprocessing layer
3. Model training layer
4. Evaluation layer

```text
Raw Dataset
    │
    ▼
Preprocessing Pipeline
    │
    ├── Centralized Dataset
    │       └── Random Forest Baseline
    │
    ├── IID Client Datasets
    │       └── Federated Learning Experiment
    │
    ├── Non-IID Client Datasets
    │       └── Federated Learning Experiment
    │
    └── Global Test Dataset
            └── Final Evaluation
```

---

## 4. Dataset Layer

The dataset is organised into traffic categories.

Expected dataset structure:

```text
data/raw/
├── Normal/
├── DoS/
├── Web/
│   ├── Command Injection/
│   └── SQL Injection/
└── TEST/
```

The selected classes are:

| Class  | Description                                                          |
| ------ | -------------------------------------------------------------------- |
| Normal | Benign network traffic                                               |
| DoS    | Denial-of-Service attack traffic                                     |
| Web    | Web-based attack traffic such as SQL injection and command injection |

The `TEST` folder is kept separate and is only used for final evaluation.

---

## 5. Preprocessing Architecture

The preprocessing pipeline prepares the raw CSV files for both centralized and federated experiments.

```text
CSV Files
   │
   ▼
Load Data with pandas
   │
   ▼
Assign Labels from Folder Names
   │
   ▼
Remove Identifier Columns
   │
   ▼
Clean Missing and Infinite Values
   │
   ▼
Keep Numeric Flow Features
   │
   ▼
Encode Labels
   │
   ▼
Scale Features using MinMaxScaler
   │
   ▼
Create Centralized, IID, Non-IID, and Test Datasets
```

### Removed Columns

Identifier-based columns are removed to avoid overfitting and improve generalisation.

Examples include:

* Source IP
* Destination IP
* Source port
* Destination port
* Protocol
* Timestamp
* Flow ID

### Output of Preprocessing

The preprocessing stage produces:

| Output               | Purpose                                     |
| -------------------- | ------------------------------------------- |
| `centralized.csv`    | Used for centralized Random Forest training |
| `iid_client1.csv`    | IID data for Client 1                       |
| `iid_client2.csv`    | IID data for Client 2                       |
| `iid_client3.csv`    | IID data for Client 3                       |
| `noniid_client1.csv` | Non-IID data for Client 1                   |
| `noniid_client2.csv` | Non-IID data for Client 2                   |
| `noniid_client3.csv` | Non-IID data for Client 3                   |
| `test.csv`           | Global test dataset                         |
| `label_encoder.pkl`  | Saved label encoder                         |
| `scaler.pkl`         | Saved feature scaler                        |

---

## 6. Centralized Baseline Architecture

The centralized baseline is used as a comparison point for the federated models.

In this setup, all training data is combined and used to train one Random Forest model.

```text
All Training Data
      │
      ▼
Centralized Preprocessing
      │
      ▼
Train / Validation Split
      │
      ▼
Random Forest Classifier
      │
      ▼
Validation Evaluation
      │
      ▼
Global Test Evaluation
```

### Purpose of the Centralized Baseline

The centralized baseline helps answer this question:

> How well can the model perform when all data is available in one location?

This result acts as an upper-bound comparison for the Federated Learning experiments.

---

## 7. Federated Learning Architecture

The Federated Learning system uses the Flower framework.

There are three simulated clients and one central server.

```text
Round 1 to Round N

Server sends global weights
        │
        ▼
Clients train locally
        │
        ▼
Clients send updated weights
        │
        ▼
Server aggregates updates using FedAvg
        │
        ▼
Updated global model is created
```

---

## 8. Flower Server

The server coordinates the Federated Learning process.

### Server Responsibilities

The server:

* Initialises the global MLP model
* Sends the global model weights to all clients
* Receives updated weights from clients
* Aggregates the updates using FedAvg
* Evaluates the global model on the test set
* Prints final metrics such as accuracy, loss, classification report, and confusion matrix

### Server Script

```text
src/fl_server_iid.py
```

Although the script name includes `iid`, it can be used for both IID and Non-IID experiments depending on which client scripts are started.

---

## 9. Federated Clients

Each client simulates an independent organisation or network environment.

### Client Responsibilities

Each client:

* Loads its own local dataset
* Splits data into local training and validation sets
* Receives global model weights from the server
* Trains the MLP model locally
* Sends updated model weights back to the server
* Keeps raw traffic data private

### IID Client Script

```text
src/fl_client_iid.py
```

This script loads IID client datasets:

```text
data/processed/iid_client1.csv
data/processed/iid_client2.csv
data/processed/iid_client3.csv
```

### Non-IID Client Script

```text
src/fl_client_noniid.py
```

This script loads Non-IID client datasets:

```text
data/processed/noniid_client1.csv
data/processed/noniid_client2.csv
data/processed/noniid_client3.csv
```

---

## 10. Federated Model Architecture

The Federated Learning model uses a lightweight Multilayer Perceptron.

```text
Input Layer:      76 numerical flow features
Hidden Layer 1:   64 neurons, ReLU activation
Hidden Layer 2:   32 neurons, ReLU activation
Output Layer:     3 neurons, Softmax activation
```

### Model Diagram

```text
Input Features
     │
     ▼
Dense Layer: 64 neurons, ReLU
     │
     ▼
Dense Layer: 32 neurons, ReLU
     │
     ▼
Dense Layer: 3 neurons, Softmax
     │
     ▼
Prediction: Normal / DoS / Web
```

### Model Configuration

| Component      | Value                            |
| -------------- | -------------------------------- |
| Model type     | Multilayer Perceptron            |
| Input size     | 76 features                      |
| Hidden layer 1 | 64 neurons                       |
| Hidden layer 2 | 32 neurons                       |
| Output classes | 3                                |
| Activation     | ReLU and Softmax                 |
| Optimiser      | Adam                             |
| Loss function  | Sparse Categorical Cross-Entropy |

---

## 11. Federated Averaging

The project uses Federated Averaging, also known as FedAvg.

FedAvg combines the model updates from all clients into one global model.

```text
Client 1 Update ──┐
                  │
Client 2 Update ──┼──► FedAvg Aggregation ──► Updated Global Model
                  │
Client 3 Update ──┘
```

### FedAvg Process

```text
1. Server sends the current global model to all clients.
2. Each client trains the model on its own local data.
3. Each client sends updated model weights to the server.
4. The server averages the client updates.
5. The averaged model becomes the new global model.
6. The process repeats for multiple rounds.
```

---

## 12. IID Experiment Architecture

In the IID experiment, all clients receive a similar distribution of traffic classes.

```text
Client 1: Normal + DoS + Web
Client 2: Normal + DoS + Web
Client 3: Normal + DoS + Web
```

The IID setup tests how Federated Learning performs when client data is balanced and similar.

Expected behaviour:

* Faster convergence
* Stable training
* Performance close to centralized learning

---

## 13. Non-IID Experiment Architecture

In the Non-IID experiment, clients receive different and imbalanced traffic distributions.

```text
Client 1: Mostly Normal traffic
Client 2: More DoS-heavy traffic
Client 3: Highly skewed traffic distribution
```

The Non-IID setup is more realistic because different organisations or network segments may observe different types of traffic.

Expected behaviour:

* Slower convergence
* More training fluctuation
* Slightly lower performance than IID
* More realistic evaluation of Federated Learning

---

## 14. Communication Flow

The communication between the server and clients is minimal.

```text
Server → Client:
Global model weights

Client → Server:
Updated model weights
```

Raw CSV files, network logs, and individual traffic records are never sent to the server.

This is the main privacy-preserving benefit of the architecture.

---

## 15. Evaluation Architecture

The global model is evaluated using a separate test set.

```text
Global Test Dataset
        │
        ▼
Final Global Model
        │
        ▼
Evaluation Metrics
        │
        ├── Accuracy
        ├── Loss
        ├── Precision
        ├── Recall
        ├── F1-score
        └── Confusion Matrix
```

The same global test set is used to compare:

* Centralized Random Forest baseline
* IID Federated Learning model
* Non-IID Federated Learning model

This ensures fair comparison across all experiments.

---

## 16. Repository Architecture

Recommended repository structure:

```text
privacy-preserving-federated-ids-flnet2023/
│
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
│
├── data/
│   ├── README.md
│   ├── raw/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
│
├── docs/
│   ├── report_summary.md
│   ├── methodology.md
│   ├── architecture.md
│   └── results.md
│
├── src/
│   ├── 00_inspect_dataset.py
│   ├── 01_prepare_data.py
│   ├── centralized_baseline.py
│   ├── cv_centralized_rf_with_reports.py
│   ├── fl_model.py
│   ├── fl_client_iid.py
│   ├── fl_client_noniid.py
│   └── fl_server_iid.py
│
├── results/
│   ├── baseline/
│   ├── iid_fl/
│   └── noniid_fl/
│
├── models/
│   └── README.md
│
└── notebooks/
    └── exploratory_analysis.ipynb
```

---

## 17. End-to-End Workflow

The complete workflow is:

```text
1. Place dataset in data/raw/
2. Inspect dataset structure
3. Preprocess data
4. Create centralized, IID, Non-IID, and test datasets
5. Train centralized Random Forest baseline
6. Start Flower server
7. Start three FL clients
8. Train global Federated Learning model
9. Evaluate global model on test set
10. Compare centralized, IID, and Non-IID results
```

---

## 18. Privacy-Preserving Design

The architecture improves privacy because raw network traffic data remains local to each client.

### Centralized Learning

```text
Client data ──► Central server ──► Model training
```

Risk:

* Raw logs are collected centrally
* Higher privacy concern
* Higher impact if central storage is breached

### Federated Learning

```text
Client data stays local ──► Only model updates are shared
```

Benefit:

* Raw data is not transferred
* Lower exposure of sensitive logs
* More suitable for collaborative intrusion detection
* Better fit for organisations with privacy or compliance requirements

---

## 19. Summary

This architecture demonstrates how Federated Learning can be used to build a privacy-preserving IDS.

The project compares a centralized Random Forest baseline with two Federated Learning scenarios:

* IID Federated Learning
* Non-IID Federated Learning

The architecture shows that multiple clients can collaboratively train a shared IDS model while keeping their raw traffic data private.

```
```
