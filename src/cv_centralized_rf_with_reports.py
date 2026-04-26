# src/cv_centralized_rf_with_reports.py
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import os
import joblib

BASE_DIR = Path(__file__).resolve().parents[1]
PREP_DIR = BASE_DIR / "preprocessed"
CENTRAL_PATH = PREP_DIR / "centralized.csv"
OUT_DIR = BASE_DIR / "cv_reports"
OUT_DIR.mkdir(exist_ok=True, parents=True)

def main():
    df = pd.read_csv(CENTRAL_PATH)
    X = df.drop(columns=["Label"]).values
    y = df["Label"].values
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    accuracies = []
    f1s = []
    fold = 1
    summaries = []

    for train_idx, val_idx in skf.split(X, y):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        clf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_val)
        print(y_pred)

        acc = accuracy_score(y_val, y_pred)
        f1 = f1_score(y_val, y_pred, average="weighted")
        accuracies.append(acc)
        f1s.append(f1)

        cm = confusion_matrix(y_val, y_pred)
        cr = classification_report(y_val, y_pred, output_dict=True)
        # Save confusion matrix and classification report per fold
        cm_path = OUT_DIR / f"confusion_fold{fold}.npy"
        np.save(cm_path, cm)
        with open(OUT_DIR / f"class_report_fold{fold}.txt", "w") as fh:
            fh.write(classification_report(y_val, y_pred, digits=4))

        print(f"[FOLD {fold}] Accuracy: {acc:.4f}, Weighted F1: {f1:.4f}")
        print(f"[FOLD {fold}] Confusion matrix:\n{cm}\n")
        summaries.append({
            "fold": fold,
            "accuracy": acc,
            "weighted_f1": f1,
            "support_DoS": int((y_val==0).sum()),
            "support_Normal": int((y_val==1).sum()),
            "support_Web": int((y_val==2).sum())
        })

        fold += 1

    # Summary
    print("\n=== CV SUMMARY ===")
    print(f"Accuracy mean={np.mean(accuracies):.6f}, std={np.std(accuracies):.6f}")
    print(f"Weighted F1 mean={np.mean(f1s):.6f}, std={np.std(f1s):.6f}")

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(OUT_DIR / "cv_summary.csv", index=False)
    # Save overall metrics
    metrics = {
        "accuracy_mean": float(np.mean(accuracies)),
        "accuracy_std": float(np.std(accuracies)),
        "weighted_f1_mean": float(np.mean(f1s)),
        "weighted_f1_std": float(np.std(f1s)),
    }
    joblib.dump(metrics, OUT_DIR / "cv_metrics.pkl")
    print(f"[SAVED] Per-fold confusion matrices and reports in: {OUT_DIR}")

if __name__ == "__main__":
    main()
