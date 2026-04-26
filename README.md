
# Privacy-Preserving Intrusion Detection using Federated Learning on FLNET-2023

## Overview

This project implements a privacy-preserving Intrusion Detection System using Federated Learning on the FLNET-2023 network traffic dataset.

Traditional machine learning-based Intrusion Detection Systems often require network traffic logs to be collected in one central location. This creates privacy, security, and compliance concerns because network logs may contain sensitive information.

This project solves that problem by using Federated Learning, where multiple clients train a shared IDS model without sharing their raw network traffic data. Each client trains locally and sends only model updates to a central Flower server.

The project compares three approaches:

- Centralized Random Forest baseline
- Federated Learning with IID client data
- Federated Learning with Non-IID client data

---

## Project Aim

The aim of this project is to design, implement, and evaluate a privacy-preserving Federated Learning-based Intrusion Detection System using flow-level network traffic data.

---

## Key Features

- End-to-end machine learning pipeline for intrusion detection
- FLNET-2023 flow-level network traffic preprocessing
- Centralized Random Forest baseline model
- Federated Learning implementation using Flower
- Three simulated federated clients
- IID and Non-IID data distribution experiments
- MLP-based federated IDS model
- Global model evaluation using a separate test set
- Confusion matrix and classification report generation
- Privacy-preserving training without sharing raw client data

---

## Technologies Used

| Category | Tools |
|---|---|
| Programming Language | Python |
| Data Processing | pandas, NumPy |
| Machine Learning | scikit-learn |
| Deep Learning | TensorFlow / Keras |
| Federated Learning | Flower |
| Visualisation | Matplotlib, Seaborn |
| Model Saving | joblib / pickle |

---

## Dataset

This project uses the FLNET-2023 flow-level network traffic dataset.

Selected traffic classes:

| Class | Description |
|---|---|
| Normal | Benign network traffic |
| DoS | Denial-of-Service attack traffic |
| Web | Web-based attacks such as SQL injection and command injection |

Expected dataset structure:

```text
data/raw/
├── Normal/
├── DoS/
├── Web/
│   ├── Command Injection/
│   └── SQL Injection/
└── TEST/
````

The raw dataset is not included in this repository due to size and licensing considerations.

Users should download the dataset from the official source and place it inside the `data/raw/` directory using the structure shown above.

---

## Repository Structure

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

## Methodology

The project follows this workflow:

```text
Raw FLNET-2023 CSV files
        │
        ▼
Dataset inspection
        │
        ▼
Data cleaning and preprocessing
        │
        ▼
Feature scaling and label encoding
        │
        ▼
Centralized, IID, Non-IID, and test dataset creation
        │
        ▼
Centralized Random Forest baseline training
        │
        ▼
Federated Learning training using Flower
        │
        ▼
Global model evaluation
        │
        ▼
Comparison of centralized, IID FL, and Non-IID FL results
```

For more detail, see:

* [Methodology](docs/methodology.md)
* [System Architecture](docs/architecture.md)
* [Results](docs/results.md)
* [Project Report Summary](docs/report_summary.md)

---

## Model Architecture

The centralized baseline uses a Random Forest classifier.

The Federated Learning model uses a lightweight Multilayer Perceptron:

```text
Input layer: 76 numerical flow features
Hidden layer 1: 64 neurons, ReLU activation
Hidden layer 2: 32 neurons, ReLU activation
Output layer: 3 neurons, Softmax activation
```

Federated Learning configuration:

| Parameter         | Value                            |
| ----------------- | -------------------------------- |
| Framework         | Flower                           |
| Aggregation       | FedAvg                           |
| Number of clients | 3                                |
| Local epochs      | 1                                |
| Rounds            | 10                               |
| Batch size        | 64                               |
| Optimiser         | Adam                             |
| Loss function     | Sparse Categorical Cross-Entropy |

---

## Results Summary

| Model                     | Learning Setup                             | Performance Summary                                  |
| ------------------------- | ------------------------------------------ | ---------------------------------------------------- |
| Centralized Random Forest | All data trained in one location           | Near-perfect performance                             |
| Federated IID MLP         | Clients have similar data distributions    | Almost matched centralized performance               |
| Federated Non-IID MLP     | Clients have imbalanced data distributions | Slight performance drop but remained highly accurate |

Approximate result summary:

| Model                      | Approximate Accuracy | Notes                                          |
| -------------------------- | -------------------: | ---------------------------------------------- |
| Centralized Baseline       |                ~100% | Upper-bound benchmark                          |
| Federated Learning IID     |              ~99.99% | Very close to centralized baseline             |
| Federated Learning Non-IID |         ~99.2%–99.3% | Slight degradation due to client heterogeneity |

The results show that Federated Learning can achieve strong intrusion detection performance while reducing the need to centralise sensitive network traffic data.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/immi999/privacy-preserving-federated-ids-flnet2023.git
cd privacy-preserving-federated-ids-flnet2023
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the environment:

For Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run the Project

### Step 1: Place the dataset

Place the FLNET-2023 dataset inside:

```text
data/raw/
```

Expected structure:

```text
data/raw/
├── Normal/
├── DoS/
├── Web/
│   ├── Command Injection/
│   └── SQL Injection/
└── TEST/
```

---

### Step 2: Inspect the dataset

```bash
python src/00_inspect_dataset.py
```

---

### Step 3: Preprocess the dataset

```bash
python src/01_prepare_data.py
```

This creates cleaned and processed files for:

* Centralized training
* IID clients
* Non-IID clients
* Global test evaluation

---

### Step 4: Train the centralized baseline

```bash
python src/centralized_baseline.py
```

Optional cross-validation:

```bash
python src/cv_centralized_rf_with_reports.py
```

---

## Running Federated Learning

### IID Federated Learning

Open four terminals.

Terminal 1: Start the server

```bash
python src/fl_server_iid.py
```

Terminal 2: Start Client 1

```bash
python src/fl_client_iid.py --cid 1
```

Terminal 3: Start Client 2

```bash
python src/fl_client_iid.py --cid 2
```

Terminal 4: Start Client 3

```bash
python src/fl_client_iid.py --cid 3
```

---

### Non-IID Federated Learning

Open four terminals.

Terminal 1: Start the server

```bash
python src/fl_server_iid.py
```

Terminal 2: Start Client 1

```bash
python src/fl_client_noniid.py --cid 1
```

Terminal 3: Start Client 2

```bash
python src/fl_client_noniid.py --cid 2
```

Terminal 4: Start Client 3

```bash
python src/fl_client_noniid.py --cid 3
```

---

## Privacy-Preserving Design

In centralized learning, all client data must be collected in one place.

```text
Client data ──► Central server ──► Model training
```

In Federated Learning, raw data stays with each client.

```text
Client data stays local ──► Only model updates are shared
```

This reduces:

* Exposure of raw network logs
* Centralized data leakage risk
* Privacy concerns
* Need for organisations to directly share sensitive traffic records

---

## Limitations

This project has some limitations:

* The federated clients are simulated.
* Only three clients are used.
* Only three traffic categories are selected.
* The dataset appears highly separable, which may contribute to very high accuracy.
* Differential privacy is not implemented.
* Secure aggregation is not implemented.
* Communication overhead is not deeply measured.

---

## Future Improvements

Possible improvements include:

* Add more attack categories.
* Test with more clients.
* Deploy clients on separate physical or cloud machines.
* Add differential privacy.
* Add secure aggregation.
* Compare FedAvg with FedProx or other FL strategies.
* Measure communication cost.
* Test on additional IDS datasets.
* Build a dashboard for visualising client and global model performance.

---

## Skills Demonstrated

This project demonstrates practical experience in:

* Cybersecurity machine learning
* Intrusion Detection Systems
* Network traffic analysis
* Data preprocessing
* Feature engineering
* Random Forest classification
* Neural network design
* Federated Learning
* Flower framework
* TensorFlow/Keras
* Model evaluation
* IID and Non-IID experiment design
* Python-based security research workflows

---

## Academic Context

This project was completed as part of an MSc Cybersecurity coursework project.

This repository contains a cleaned and reproducible portfolio version of the project. Personal identifiers, university IDs, raw dataset files, and assessment-specific declaration materials have been removed.

---

## Disclaimer

This project is for educational and research purposes only. It is not intended to be used as a production-ready intrusion detection system without further testing, validation, and security hardening.

---

## Author

**Imran Hossain**

MSc Cybersecurity Student
LinkedIn: [imranhossain989](https://www.linkedin.com/in/imranhossain989)

---

## License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.

