# Methodology

## 1. Overview

This project follows a complete machine learning and Federated Learning pipeline for building a privacy-preserving Intrusion Detection System using the FLNET-2023 dataset.

The methodology includes:

- Dataset inspection
- Data loading and label assignment
- Data cleaning and preprocessing
- Centralized baseline model training
- Federated Learning setup using Flower
- IID and Non-IID client experiments
- Model evaluation using a separate test set

The main goal is to compare traditional centralized machine learning with Federated Learning while keeping client data local.

---

## 2. Dataset Structure

The project uses flow-level network traffic data from FLNET-2023. The dataset is organised into folders based on traffic type.

Expected dataset structure:

```text
data/raw/
├── Normal/
├── DoS/
├── Web/
│   ├── Command Injection/
│   └── SQL Injection/
└── TEST/



The selected traffic categories are:

Category	Description
Normal	Benign network traffic
DoS	Denial-of-Service attack traffic
Web	Web-based attack traffic, including SQL injection and command injection

The TEST folder is kept separate and is only used for final model evaluation.

3. Label Assignment

The original CSV files do not contain ready-to-use class labels. Therefore, labels are assigned based on the folder name.

Folder	Assigned Label
Normal/	Normal
DoS/	DoS
Web/Command Injection/	Web
Web/SQL Injection/	Web

The labels are later encoded into numeric values for machine learning.

Example label mapping:

DoS    -> 0
Normal -> 1
Web    -> 2

4. Data Loading

All relevant CSV files are loaded using pandas.

The loading process:

Read CSV files from each selected folder.
Assign a label based on the folder name.
Merge all selected CSV files into a single dataset.
Create separate datasets for centralized training, IID Federated Learning, Non-IID Federated Learning, and testing.

The centralized dataset combines all selected training files into one dataset.
The federated setup keeps client-specific data separate to simulate distributed organisations or devices.

5. Data Cleaning

Before training, the dataset is cleaned to remove unnecessary or non-numeric features.

The following types of columns are removed:

Source IP address
Destination IP address
Source port
Destination port
Protocol
Timestamp
Flow ID
Other identifier-based fields

These columns are removed because they can cause the model to overfit to environment-specific identifiers rather than learning general network behaviour.

Rows containing missing values, infinite values, or invalid numeric entries are also removed or corrected.

6. Feature Selection

After cleaning, only numerical flow-level features are kept for model training.

Examples of selected feature types include:

Flow duration
Packet counts
Packet length statistics
Inter-arrival time statistics
Bytes per second
Packets per second
TCP flag counts
Active and idle time statistics

These features are suitable for machine learning-based intrusion detection because they represent behavioural patterns in network traffic.

7. Feature Scaling

The numerical features are normalised using MinMaxScaler.

The scaler transforms feature values into the range:

0 to 1

This is useful because flow-level features can have very different scales. For example, flow duration may have very large values, while TCP flag counts may be small.

Scaling helps:

Improve neural network stability
Reduce feature dominance
Make training more consistent across clients
Support fair comparison between centralized and federated models

The scaler is fitted on the training data and then reused for client datasets and the test set.

8. Train, Validation, and Test Split

The project uses three types of data splits:

Split	Purpose
Training set	Used to train the model
Validation set	Used to evaluate model performance during development
Test set	Used only for final evaluation

For the centralized baseline, the combined dataset is split into training and validation sets.

For Federated Learning, each client creates its own local training and validation split.

The global test set remains separate and is not used during training.

9. Centralized Baseline Model

A centralized Random Forest model is trained as the baseline.

In this approach, all training data is combined and trained in one location.

The centralized baseline is important because it provides an upper-bound comparison for the Federated Learning models.

Baseline Model
Component	Configuration
Model	Random Forest Classifier
Input	Cleaned and scaled flow-level features
Output	3 traffic classes: Normal, DoS, Web
Evaluation	Validation set and global test set

The model is evaluated using:

Accuracy
Classification report
Confusion matrix

Cross-validation is also used to check whether the baseline result is stable across different folds.

10. Federated Learning Design

Federated Learning is implemented using the Flower framework.

The system uses a client-server architecture.

Client 1 ──┐
           │
Client 2 ──┼──► Flower Server ──► Global IDS Model
           │
Client 3 ──┘

Each client trains the model using its own local data.
The clients do not send raw network traffic data to the server.
Instead, they send model weight updates.

The server aggregates the updates and produces a global model.

11. Federated Model Architecture

A lightweight Multilayer Perceptron is used for the Federated Learning experiments.

Input layer: 76 numerical features
Hidden layer 1: 64 neurons, ReLU activation
Hidden layer 2: 32 neurons, ReLU activation
Output layer: 3 neurons, Softmax activation

The model is designed to be small and efficient so that it can train quickly in a simulated federated environment.

Model Configuration
Component	Value
Model	MLP
Optimiser	Adam
Loss function	Sparse Categorical Cross-Entropy
Output classes	3
Framework	TensorFlow/Keras
12. Federated Learning Strategy

The project uses Federated Averaging, also known as FedAvg.

The training process works as follows:

1. The server initialises the global model.
2. The server sends model weights to all clients.
3. Each client trains the model locally.
4. Each client sends updated weights back to the server.
5. The server averages the client updates.
6. The updated global model is redistributed.
7. The process repeats for multiple rounds.

FedAvg allows multiple clients to collaboratively train a model without directly sharing their datasets.

13. IID Federated Learning Experiment

In the IID setup, each client receives a similar distribution of traffic classes.

This means each client has a mixed sample of:

Normal traffic
DoS traffic
Web attack traffic

The IID experiment is used to test whether Federated Learning can achieve performance close to centralized learning when client data distributions are balanced.

14. Non-IID Federated Learning Experiment

In the Non-IID setup, each client receives a different and uneven distribution of traffic classes.

Example client distribution:

Client	Data Pattern
Client 1	Mostly normal traffic
Client 2	More attack-heavy traffic
Client 3	Highly skewed traffic distribution

This setup is more realistic because different organisations, devices, or network segments may observe different types of traffic.

The Non-IID experiment tests how well the Federated Learning model performs under client data imbalance and heterogeneity.

15. Federated Training Configuration

The Federated Learning experiments use the following general configuration:

Parameter	Value
Number of clients	3
FL framework	Flower
Aggregation strategy	FedAvg
Number of rounds	10
Local epochs	1
Batch size	64
Optimiser	Adam
Evaluation dataset	Global test set
16. Evaluation Metrics

All models are evaluated using standard classification metrics.

Metric	Purpose
Accuracy	Measures overall correct predictions
Precision	Measures how many predicted attacks/classes were correct
Recall	Measures how many actual attacks/classes were detected
F1-score	Balances precision and recall
Confusion matrix	Shows correct and incorrect predictions per class
Loss	Measures model error during training/evaluation

The same global test set is used to compare the centralized, IID Federated Learning, and Non-IID Federated Learning models.

17. Reproducibility Workflow

To reproduce the project, run the scripts in the following order:

# 1. Inspect dataset structure
python src/00_inspect_dataset.py

# 2. Prepare cleaned datasets and client splits
python src/01_prepare_data.py

# 3. Train centralized baseline model
python src/centralized_baseline.py

# 4. Run cross-validation for centralized model
python src/cv_centralized_rf_with_reports.py

For IID Federated Learning:

# Terminal 1: Start server
python src/fl_server_iid.py

# Terminal 2: Start client 1
python src/fl_client_iid.py --cid 1

# Terminal 3: Start client 2
python src/fl_client_iid.py --cid 2

# Terminal 4: Start client 3
python src/fl_client_iid.py --cid 3

For Non-IID Federated Learning:

# Terminal 1: Start server
python src/fl_server_iid.py

# Terminal 2: Start client 1
python src/fl_client_noniid.py --cid 1

# Terminal 3: Start client 2
python src/fl_client_noniid.py --cid 2

# Terminal 4: Start client 3
python src/fl_client_noniid.py --cid 3
18. Privacy-Preserving Aspect

The privacy-preserving design comes from the Federated Learning setup.

In centralized learning, all network traffic data must be collected in one place.
In Federated Learning, raw traffic data stays with each client.

Only model updates are shared with the server.

This reduces:

Raw data exposure
Centralized data leakage risk
Privacy concerns linked to network logs
The need for organisations to share sensitive traffic records
19. Limitations

The project has some limitations:

The clients are simulated rather than deployed on real distributed machines.
Only three traffic categories are used.
The dataset appears highly separable, which may contribute to very high accuracy.
Advanced privacy techniques such as differential privacy and secure aggregation are not implemented.
Communication cost is not deeply measured.
The experiment uses a limited number of clients.
20. Future Improvements

Possible future improvements include:

Add more attack categories.
Test with more federated clients.
Deploy clients on separate physical or cloud machines.
Add differential privacy.
Add secure aggregation.
Compare FedAvg with other FL strategies such as FedProx.
Measure communication overhead.
Evaluate the model on other IDS datasets.
Build a dashboard for visualising client performance and global model results.