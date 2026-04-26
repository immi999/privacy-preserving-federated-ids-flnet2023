# src/centralized_baseline.py
from pathlib import Path
import joblib
import hashlib
from collections import Counter
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE

# ==============================
# PATHS
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]
PREP_DIR = BASE_DIR / "preprocessed"

CENTRALIZED_PATH = PREP_DIR / "centralized.csv"
TEST_PATH = PREP_DIR / "test.csv"
ENCODER_PATH = PREP_DIR / "label_encoder.pkl"

# User-tunable knobs (adjust if needed)
MAX_MAJOR_TARGET = 30000       # maximum number of majority samples after undersampling
DOS_RATIO = 0.6                # fraction of majority target to assign to DoS after SMOTE
WEB_RATIO = 0.2                # fraction of majority target to assign to Web after SMOTE
DO_OVERLAP_CHECK = True       # whether to compute row-overlap between centralized and test (can be slow)


def row_hashes(df: pd.DataFrame) -> pd.Series:
    """Compute md5 hash for each row (string-joined)."""
    # convert to string to make hash stable
    joined = df.astype(str).agg('|'.join, axis=1)
    return joined.apply(lambda s: hashlib.md5(s.encode()).hexdigest())


def load_data():
    print(f"[INFO] Loading centralized data from: {CENTRALIZED_PATH}")
    df = pd.read_csv(CENTRALIZED_PATH)
    print(f"[INFO] Centralized shape: {df.shape}")

    print(f"[INFO] Loading test data from: {TEST_PATH}")
    df_test = pd.read_csv(TEST_PATH)
    print(f"[INFO] Test shape: {df_test.shape}")

    # quick sanity: ensure Label column exists
    if "Label" not in df.columns or "Label" not in df_test.columns:
        raise ValueError("Label column missing from centralized.csv or test.csv")

    # Optionally check exact duplicate rows between central and test to detect leakage
    if DO_OVERLAP_CHECK:
        try:
            t0 = time.time()
            print("[INFO] Computing exact row-hash overlap between centralized and test (this may take a while)...")
            h_central = set(row_hashes(df))
            h_test = set(row_hashes(df_test))
            overlap = len(h_central.intersection(h_test))
            print(f"[WARN] Overlapping exact rows between centralized and test: {overlap}")
            print(f"[INFO] Overlap check took {time.time()-t0:.1f}s")
        except Exception as e:
            print(f"[WARN] Overlap check failed/skipped due to: {e}")

    # Separate features and labels
    X = df.drop(columns=["Label"])
    y = df["Label"].astype(int)

    X_test = df_test.drop(columns=["Label"])
    y_test = df_test["Label"].astype(int)

    print("\n[INFO] Centralized label distribution:")
    print(y.value_counts())

    print("\n[INFO] Test label distribution:")
    print(y_test.value_counts())

    return X, y, X_test, y_test


def compute_sampling_targets(y_train: pd.Series, max_major_target=MAX_MAJOR_TARGET):
    """
    Compute undersample/oversample targets:
      - reduce majority to at most max_major_target
      - produce minority targets as fractions of majority target (DOS_RATIO, WEB_RATIO)
    Returns:
      maj_label, sampling_rus_dict, smote_targets_dict
    """
    counts = Counter(y_train)
    # find majority label
    maj_label, maj_count = max(counts.items(), key=lambda t: t[1])
    # choose majority target
    maj_target = min(max_major_target, maj_count)
    # compute minority targets (at least their current count)
    # we'll identify labels except maj_label, distribute according to DOS_RATIO/WEB_RATIO heuristics
    other_labels = [lbl for lbl in counts.keys() if lbl != maj_label]
    # We'll map based on the convention observed in your project:
    # 0 -> DoS, 1 -> Normal (likely majority), 2 -> Web
    # but we compute generically: prefer to set targets for known labels 0 and 2 if present
    # default fallback: split remaining among other labels evenly
    targets = {}
    # conservative minima: keep at least the original counts to avoid downsampling minorities below original
    if 0 in counts and 2 in counts:
        targets[0] = max(counts[0], int(maj_target * DOS_RATIO))
        targets[2] = max(counts[2], int(maj_target * WEB_RATIO))
    else:
        # generic: split evenly among other labels
        for i, lbl in enumerate(other_labels):
            frac = 0.5 if len(other_labels) == 2 else (1.0 / len(other_labels))
            targets[lbl] = max(counts[lbl], int(maj_target * frac))
    # Return undersample dict (only for majority) and smote targets for minorities
    rus_strategy = {maj_label: maj_target}
    smote_strategy = targets
    print(f"[INFO] Counts (train): {counts}")
    print(f"[INFO] Majority label: {maj_label} -> target {maj_target}")
    print(f"[INFO] RandomUnderSampler strategy: {rus_strategy}")
    print(f"[INFO] SMOTE strategy: {smote_strategy}")
    return rus_strategy, smote_strategy


def train_random_forest_pipeline(X, y):
    """
    Train pipeline: RandomUnderSampler -> SMOTE -> RandomForest
    Resampling is applied only on the training split.
    """
    print("\n[INFO] Splitting train/validation (80/20, stratified)...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print(f"[INFO] Train shape: {X_train.shape}, Val shape: {X_val.shape}")

    # compute sampling targets based on X_train counts
    rus_strategy, smote_targets = compute_sampling_targets(y_train)

    # build pipeline
    rus = RandomUnderSampler(sampling_strategy=rus_strategy, random_state=42)
    smote = SMOTE(random_state=42, sampling_strategy=smote_targets)
    rf = RandomForestClassifier(n_estimators=150, n_jobs=-1, random_state=42)

    pipeline = ImbPipeline(steps=[("rus", rus), ("smote", smote), ("rf", rf)])

    print("[INFO] Fitting pipeline (under-sample -> SMOTE -> RandomForest). This may take some time...")
    t0 = time.time()
    pipeline.fit(X_train, y_train)
    print(f"[INFO] Pipeline fit completed in {time.time()-t0:.1f}s")

    return pipeline, X_val, y_val


def evaluate_model(model, X, y, label_encoder, title="Evaluation"):
    print(f"\n========== {title} ==========")
    y_pred = model.predict(X)

    acc = accuracy_score(y, y_pred)
    print(f"Accuracy: {acc:.4f}")

    print("\nClassification report:")
    # label_encoder.classes_ should align with encoded integer labels 0..n-1
    target_names = list(label_encoder.classes_)
    print(classification_report(y, y_pred, target_names=target_names, digits=4))

    cm = confusion_matrix(y, y_pred)
    print("Confusion matrix (rows = true, cols = predicted):")
    print(cm)

    print("\nLabel mapping (from LabelEncoder):")
    for idx, cls in enumerate(label_encoder.classes_):
        print(f"  {idx} -> {cls}")

    return acc, cm


def main():
    print(f"[INFO] BASE_DIR = {BASE_DIR}")
    print(f"[INFO] PREP_DIR = {PREP_DIR}")

    # Load data
    X, y, X_test, y_test = load_data()

    # Load label encoder (for mapping back 0/1/2 -> DoS/Normal/Web)
    print(f"\n[INFO] Loading LabelEncoder from: {ENCODER_PATH}")
    label_encoder = joblib.load(ENCODER_PATH)
    print("[INFO] Classes:", list(label_encoder.classes_))

    # Train model (pipeline)
    model_pipeline, X_val, y_val = train_random_forest_pipeline(X, y)

    # Evaluate on validation split
    evaluate_model(model_pipeline, X_val, y_val, label_encoder, title="Validation Set")

    # Evaluate on held-out TEST set
    evaluate_model(model_pipeline, X_test, y_test, label_encoder, title="Global TEST Set")

    # Save the pipeline (it contains the resampling steps + RF)
    model_path = PREP_DIR / "centralized_rf_pipeline.pkl"
    joblib.dump(model_pipeline, model_path)
    print(f"\n[SAVE] Centralized RandomForest pipeline saved to: {model_path}")

    print("\n[DONE] Centralized baseline evaluation finished.")


if __name__ == "__main__":
    main()
