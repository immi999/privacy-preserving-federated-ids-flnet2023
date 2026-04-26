
# Project Report Summary

## Project Title

Privacy-Preserving Intrusion Detection using Federated Learning on FLNET-2023

---

## 1. Project Overview

This project focuses on building a privacy-preserving Intrusion Detection System using Federated Learning.

Traditional machine learning-based intrusion detection often requires collecting network traffic data in one central location. This can create privacy, security, and compliance concerns because network traffic logs may contain sensitive information.

To address this issue, this project uses Federated Learning, where multiple clients train a shared model collaboratively without sharing their raw data. Each client trains the model locally and sends only model updates to the central server.

The project compares three approaches:

- Centralized machine learning baseline
- Federated Learning with IID data distribution
- Federated Learning with Non-IID data distribution

---

## 2. Aim of the Project

The aim of this project is to design, implement, and evaluate a privacy-preserving Federated Learning-based Intrusion Detection System using flow-level network traffic data.

---

## 3. Project Objectives

The main objectives of the project are:

- Build a centralized machine learning baseline for intrusion detection.
- Implement a Federated Learning system using the Flower framework.
- Simulate three federated clients.
- Train and evaluate the model under IID data distribution.
- Train and evaluate the model under Non-IID data distribution.
- Compare centralized and federated model performance.
- Analyse the impact of data imbalance and client heterogeneity.
- Discuss the privacy benefits of Federated Learning for intrusion detection.

---

## 4. Dataset

The project uses the FLNET-2023 flow-level network traffic dataset.

The selected traffic categories are:

| Class | Description |
|---|---|
| Normal | Benign network traffic |
| DoS | Denial-of-Service attack traffic |
| Web | Web-based attack traffic, including SQL injection and command injection |

The dataset contains flow-level features such as:

- Flow duration
- Packet counts
- Packet length statistics
- Inter-arrival time statistics
- Bytes per second
- Packets per second
- TCP flag counts
- Active and idle time statistics

The raw dataset is not included in this repository due to size and licensing considerations.

---

## 5. Data Preprocessing

The preprocessing stage prepares the raw CSV files for machine learning and Federated Learning experiments.

The preprocessing pipeline includes:

1. Loading CSV files from different traffic folders.
2. Assigning labels based on folder names.
3. Combining selected CSV files.
4. Removing non-useful identifier columns.
5. Cleaning missing and infinite values.
6. Keeping only numerical flow-level features.
7. Encoding labels into numeric format.
8. Scaling features using MinMaxScaler.
9. Creating centralized, IID, Non-IID, and test datasets.

Identifier-based fields such as IP addresses, ports, timestamps, protocols, and flow IDs are removed to reduce overfitting and improve generalisation.

---

## 6. Centralized Baseline

A Random Forest classifier is used as the centralized baseline model.

In the centralized setup, all training data is combined and trained in one location. This gives a strong comparison point for the Federated Learning models.

The centralized baseline is evaluated using:

- Accuracy
- Classification report
- Confusion matrix
- Cross-validation

The centralized model achieved near-perfect performance, showing that the selected dataset features are highly learnable and separable.

---

## 7. Federated Learning Approach

Federated Learning is implemented using the Flower framework.

The system uses a client-server architecture:

- The server coordinates the training process.
- Three clients simulate separate organisations or network environments.
- Each client trains locally using its own data.
- Clients send model weight updates to the server.
- The server aggregates client updates using Federated Averaging.

Raw network traffic data is not shared with the server.

---

## 8. Federated Model

The Federated Learning model uses a lightweight Multilayer Perceptron.

Model architecture:

```text
Input layer: 76 numerical features
Hidden layer 1: 64 neurons, ReLU activation
Hidden layer 2: 32 neurons, ReLU activation
Output layer: 3 neurons, Softmax activation
````

Model configuration:

| Component           | Value                            |
| ------------------- | -------------------------------- |
| Model               | Multilayer Perceptron            |
| Framework           | TensorFlow/Keras                 |
| Federated framework | Flower                           |
| Aggregation         | FedAvg                           |
| Optimiser           | Adam                             |
| Loss function       | Sparse Categorical Cross-Entropy |
| Number of clients   | 3                                |
| Training rounds     | 10                               |
| Local epochs        | 1                                |
| Batch size          | 64                               |

---

## 9. IID Federated Learning Experiment

In the IID setup, each client receives a similar distribution of Normal, DoS, and Web traffic.

This simulates a balanced federated environment where all clients have similar data patterns.

The IID Federated Learning model achieved performance very close to the centralized baseline, showing that Federated Learning can maintain strong detection performance when client data distributions are similar.

---

## 10. Non-IID Federated Learning Experiment

In the Non-IID setup, each client receives a different and imbalanced distribution of traffic classes.

This simulates a more realistic environment where different organisations or devices may observe different types of traffic.

Example:

| Client   | Data Pattern                       |
| -------- | ---------------------------------- |
| Client 1 | Mostly normal traffic              |
| Client 2 | More attack-heavy traffic          |
| Client 3 | Highly skewed traffic distribution |

The Non-IID model showed a slight performance drop compared with the IID setup. This was expected because client data imbalance can cause slower convergence and model instability.

However, the final performance remained strong, showing that the Federated Learning model was still effective under heterogeneous data conditions.

---

## 11. Results Summary

| Model                      | Performance Summary                                                      |
| -------------------------- | ------------------------------------------------------------------------ |
| Centralized Random Forest  | Near-perfect performance and used as the upper-bound baseline            |
| Federated Learning IID     | Very close to centralized performance                                    |
| Federated Learning Non-IID | Slight degradation due to client heterogeneity but still highly accurate |

Main findings:

* Centralized learning achieved the best performance.
* IID Federated Learning almost matched centralized learning.
* Non-IID Federated Learning had slightly more errors but remained effective.
* Federated Learning reduced the need to share raw network data.
* The MLP model performed well in the Federated Learning setup.

---

## 12. Key Discussion Points

The project shows that Federated Learning is suitable for privacy-preserving intrusion detection.

The results suggest that when clients have balanced data, Federated Learning can perform almost as well as centralized learning. When clients have imbalanced data, performance may drop slightly, but the approach remains practical.

The high accuracy may also be influenced by the dataset being highly separable. This means the traffic classes had clear feature differences, making them easier for the model to classify.

---

## 13. Privacy Benefit

The main privacy advantage of Federated Learning is that raw traffic data remains local.

In a centralized approach, clients need to send their data to a central location. This increases the risk of exposing sensitive logs.

In the federated approach:

* Raw network logs stay with each client.
* Only model updates are shared.
* Organisations can collaborate without directly exchanging sensitive traffic data.
* The risk linked to centralised data collection is reduced.

---

## 14. Limitations

The project has some limitations:

* The clients are simulated rather than deployed in real organisations.
* Only three clients are used.
* Only three traffic categories are included.
* The dataset appears highly separable, which may explain the very high accuracy.
* Differential privacy is not implemented.
* Secure aggregation is not implemented.
* Communication cost is not deeply analysed.

---

## 15. Future Improvements

Future work could improve this project by:

* Adding more attack categories.
* Testing with more clients.
* Deploying clients on separate machines or cloud instances.
* Comparing FedAvg with FedProx or other federated strategies.
* Adding differential privacy.
* Adding secure aggregation.
* Measuring communication overhead.
* Testing the model on other IDS datasets.
* Building a dashboard to visualise training progress and model performance.

---

## 16. Skills Demonstrated

This project demonstrates practical skills in:

* Cybersecurity machine learning
* Intrusion Detection Systems
* Network traffic analysis
* Dataset preprocessing
* Feature engineering
* Model evaluation
* Random Forest classification
* Neural network design
* Federated Learning
* Flower framework
* TensorFlow/Keras
* Python-based ML pipelines
* IID and Non-IID experiment design

---

## 17. Conclusion

This project demonstrates that Federated Learning can be used to build a privacy-preserving Intrusion Detection System.

The centralized Random Forest baseline achieved the strongest performance, while the IID Federated Learning model achieved very similar results. The Non-IID Federated Learning model showed a slight drop in performance but remained highly accurate.

Overall, the project shows that Federated Learning is a practical approach for collaborative intrusion detection where organisations want to improve security detection without sharing raw network traffic data.


