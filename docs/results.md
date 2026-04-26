
# Results

## 1. Overview

This document summarises the experimental results of the project.

The project compares three model settings:

- Centralized Random Forest baseline
- Federated Learning with IID client data
- Federated Learning with Non-IID client data

The same global test set is used to compare the models fairly.

---

## 2. Evaluation Metrics

The models are evaluated using the following metrics:

| Metric | Description |
|---|---|
| Accuracy | Measures the percentage of correct predictions |
| Precision | Measures how many predicted class samples were correct |
| Recall | Measures how many actual class samples were correctly detected |
| F1-score | Balances precision and recall |
| Loss | Measures model error |
| Confusion matrix | Shows correct and incorrect predictions for each class |

---

## 3. Dataset Summary

The project uses three selected traffic classes:

| Class | Description |
|---|---|
| Normal | Benign network traffic |
| DoS | Denial-of-Service attack traffic |
| Web | Web-based attacks such as SQL injection and command injection |

The processed centralized dataset contains:

| Dataset | Samples |
|---|---:|
| Centralized training and validation dataset | 433,628 |
| Global test dataset | 204,027 |

Class distribution in the centralized dataset:

| Class | Samples |
|---|---:|
| DoS | 39,869 |
| Normal | 389,919 |
| Web | 3,840 |

Class distribution in the test dataset:

| Class | Samples |
|---|---:|
| DoS | 12,092 |
| Normal | 189,836 |
| Web | 2,099 |

---

## 4. Centralized Baseline Results

The centralized baseline uses a Random Forest classifier.

In this setup, all training data is combined in one location. This gives a strong comparison point for the Federated Learning models.

### Centralized Model Summary

| Item | Value |
|---|---|
| Model | Random Forest Classifier |
| Training approach | Centralized learning |
| Input features | 76 numerical flow-level features |
| Classes | DoS, Normal, Web |
| Evaluation | Validation set and global test set |

### Result Interpretation

The centralized Random Forest model achieved near-perfect performance.

This indicates that the selected classes in the dataset are highly separable using flow-level features such as packet statistics, duration, inter-arrival time, and TCP flag counts.

The centralized model acts as the upper-bound benchmark because it has access to all training data in one location.

---

## 5. Federated Learning - IID Results

The IID Federated Learning experiment uses three clients with similar class distributions.

Each client receives a balanced mix of:

- Normal traffic
- DoS traffic
- Web attack traffic

### IID Configuration

| Item | Value |
|---|---|
| Number of clients | 3 |
| FL framework | Flower |
| Aggregation strategy | FedAvg |
| Model | MLP |
| Local epochs | 1 |
| Training rounds | 10 |
| Batch size | 64 |

### IID Result Summary

| Metric | Result |
|---|---|
| Accuracy | Approximately 99.99% |
| Test loss | Very low |
| Convergence | Fast, around 1–2 rounds |
| Total errors | Very few misclassifications |

### Result Interpretation

The IID Federated Learning model achieved performance very close to the centralized baseline.

This shows that when clients have similar data distributions, Federated Learning can train an effective global IDS model without sharing raw network traffic data.

The IID result supports the idea that Federated Learning can preserve performance while improving privacy.

---

## 6. Federated Learning - Non-IID Results

The Non-IID Federated Learning experiment uses three clients with different and imbalanced class distributions.

This setup is more realistic because different organisations or network segments may observe different traffic patterns.

### Example Non-IID Client Distribution

| Client | Data Pattern |
|---|---|
| Client 1 | Mostly normal traffic |
| Client 2 | More attack-heavy traffic |
| Client 3 | Highly skewed distribution with limited attack samples |

### Non-IID Configuration

| Item | Value |
|---|---|
| Number of clients | 3 |
| FL framework | Flower |
| Aggregation strategy | FedAvg |
| Model | MLP |
| Local epochs | 1 |
| Training rounds | 10 |
| Batch size | 64 |

### Non-IID Result Summary

| Metric | Result |
|---|---|
| Accuracy | Approximately 99.2% to 99.3% |
| Test loss | Low |
| Convergence | Slower than IID |
| Training behaviour | More fluctuation due to client heterogeneity |
| Total errors | More than IID but still low |

### Result Interpretation

The Non-IID model showed a slight performance drop compared with the IID model.

This is expected because Non-IID data creates challenges such as:

- Client drift
- Class imbalance
- Uneven local learning
- Slower global convergence
- Higher variation between client updates

Despite these challenges, the global model still achieved strong performance. This suggests that the Federated Learning approach is practical even when clients have different traffic distributions.

---

## 7. Model Comparison

| Model | Learning Setup | Performance Summary |
|---|---|---|
| Centralized Random Forest | All data trained in one location | Best upper-bound performance |
| Federated IID MLP | Clients have similar data distributions | Almost matched centralized performance |
| Federated Non-IID MLP | Clients have imbalanced data distributions | Slight performance drop but still strong |

---

## 8. Accuracy Comparison

| Model | Approximate Accuracy | Notes |
|---|---:|---|
| Centralized Baseline | ~100% | Strongest benchmark |
| Federated Learning IID | ~99.99% | Very close to centralized baseline |
| Federated Learning Non-IID | ~99.2%–99.3% | Slight degradation due to data heterogeneity |

---

## 9. Key Findings

The main findings are:

- The centralized Random Forest model achieved the strongest performance.
- IID Federated Learning achieved almost the same performance as centralized learning.
- Non-IID Federated Learning had slightly lower performance but remained highly accurate.
- Client data imbalance affected convergence and stability.
- Federated Learning reduced the need to share raw network traffic data.
- The MLP model was suitable for the federated IDS setup.
- The dataset appears highly separable, which may explain the very high accuracy.

---

## 10. Why the Accuracy Was Very High

The results were very high because the selected dataset features made the classes easier to separate.

Possible reasons include:

### 1. Highly separable traffic patterns

DoS, Normal, and Web traffic had clear differences in flow-level behaviour.

Useful features may include:

- Flow duration
- Packet rate
- Packet length statistics
- Inter-arrival time
- TCP flag counts
- Bytes per second
- Packets per second

### 2. Large dataset size

The dataset contains a large number of samples, which helps the model learn stable patterns.

### 3. Strong preprocessing

Cleaning, feature selection, label encoding, and scaling improved model quality.

### 4. Class balancing

Balancing techniques helped the model learn minority classes more effectively.

---

## 11. Privacy and Practical Impact

The Federated Learning results are important because they show that strong IDS performance can be achieved without centralising raw data.

In a real-world scenario, this could help:

- Banks collaborate without sharing sensitive logs
- Healthcare organisations train shared IDS models while protecting patient-related systems
- Multiple branches of a company improve detection together
- IoT or edge devices contribute to a global IDS model without exposing local traffic

---

## 12. Limitations of Results

The results should be interpreted carefully.

Limitations include:

- The clients are simulated, not deployed in separate real networks.
- Only three clients are used.
- Only three traffic categories are selected.
- The dataset appears highly separable.
- Advanced privacy methods such as differential privacy are not included.
- Secure aggregation is not implemented.
- Communication cost is not deeply measured.
- The results may not directly generalise to all real-world network environments.

---

## 13. Suggested Result Files

The following files can be stored in the `results/` folder:

```text
results/
├── baseline/
│   ├── metrics.csv
│   └── confusion_matrix.png
│
├── iid_fl/
│   ├── metrics.csv
│   └── confusion_matrix.png
│
└── noniid_fl/
    ├── metrics.csv
    ├── confusion_matrix.png
    └── accuracy_progression.png
````

These files can make the repository easier to understand for recruiters, supervisors, or technical reviewers.

---

## 14. Final Interpretation

The results show that Federated Learning is a strong approach for privacy-preserving intrusion detection.

The IID Federated Learning model almost matched the centralized baseline, while the Non-IID model showed only a small performance drop. This suggests that a shared IDS model can be trained across distributed clients without requiring raw traffic logs to be shared.

Overall, the project demonstrates the practical value of Federated Learning for collaborative cybersecurity monitoring.

