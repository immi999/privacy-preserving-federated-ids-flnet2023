
# Requirements

## 1. Overview

This document lists the software, libraries, hardware, and dataset requirements needed to run this project.

The project uses Python for data preprocessing, centralized machine learning, and Federated Learning experiments.

---

## 2. System Requirements

Recommended system configuration:

| Component | Recommended Specification |
|---|---|
| Operating System | Windows 10/11, macOS, or Linux |
| CPU | Intel i5/i7 or equivalent |
| RAM | 16 GB recommended |
| Storage | SSD recommended |
| Python Version | Python 3.10 or 3.11 |

The project can run on a normal laptop, but preprocessing and model training may take longer on low-memory systems.

---

## 3. Python Environment

It is recommended to use a virtual environment.

Create a virtual environment:

```bash
python -m venv venv
````

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

---

## 4. Python Libraries

The main Python libraries required are:

| Library          | Purpose                                                 |
| ---------------- | ------------------------------------------------------- |
| pandas           | Loading and processing CSV files                        |
| numpy            | Numerical operations                                    |
| scikit-learn     | Machine learning, preprocessing, metrics, Random Forest |
| imbalanced-learn | Class balancing using techniques such as SMOTE          |
| tensorflow       | Building and training the MLP model                     |
| flwr             | Federated Learning using Flower                         |
| matplotlib       | Plotting graphs and confusion matrices                  |
| seaborn          | Visualising confusion matrices and distributions        |
| joblib           | Saving and loading models, scalers, and encoders        |
| pyyaml           | Reading configuration files, if used                    |

---

## 5. Install Dependencies

Install all required packages using:

```bash
pip install -r requirements.txt
```

Recommended `requirements.txt` content:

```txt
pandas
numpy
scikit-learn
imbalanced-learn
tensorflow
flwr
matplotlib
seaborn
joblib
pyyaml
```

For a more fixed environment, you can generate exact package versions from your working environment:

```bash
pip freeze > requirements.txt
```

---

## 6. Dataset Requirement

This project requires the FLNET-2023 flow-level network traffic dataset.

The dataset should be placed inside:

```text
data/raw/
```

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

The raw dataset is not included in this repository due to size and licensing considerations.

Users should download the dataset from the official source and place it in the required folder structure before running the project.

---

## 7. Processed Data Outputs

After running the preprocessing script, the following processed files may be created:

```text
data/processed/
├── centralized.csv
├── iid_client1.csv
├── iid_client2.csv
├── iid_client3.csv
├── noniid_client1.csv
├── noniid_client2.csv
├── noniid_client3.csv
├── test.csv
├── label_encoder.pkl
└── scaler.pkl
```

These files are generated locally and should usually not be uploaded to GitHub if they are large.

---

## 8. Model Outputs

The training scripts may generate model files such as:

```text
models/
├── centralized_rf_model.pkl
└── federated_global_model.h5
```

Large model files should only be uploaded if necessary. Otherwise, users can reproduce them by running the training scripts.

---

## 9. Running Requirement Check

After installing dependencies, check that the main packages are installed correctly:

```bash
python -c "import pandas, numpy, sklearn, tensorflow, flwr; print('All main packages imported successfully')"
```

---

## 10. Notes

* Use Python 3.10 or 3.11 for better compatibility.
* TensorFlow installation may vary depending on operating system and hardware.
* The raw dataset must be downloaded separately.
* Federated Learning experiments require running one server and three clients in separate terminals.
* At least 16 GB RAM is recommended for smoother preprocessing and training.

