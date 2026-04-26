import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import StratifiedKFold
import joblib


# ==============================
# CONFIG
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1] / "data"
PREP_DIR = Path(__file__).resolve().parents[1] / "preprocessed"
PREP_DIR.mkdir(exist_ok=True, parents=True)

CLASS_FOLDERS = {
    "Normal": "Normal",
    "DoS": "DoS",
    "Web": "Web",
}

# UPDATED — Added XSS
WEB_SUBFOLDERS = ["Command Injection", "SQL Injection", "XSS"]

CLIENT_IDS = ["1", "2", "3"]  # Dataset-1/2/3


# ==============================
# HELPERS
# ==============================
def load_train_full() -> pd.DataFrame:
    """Load all training data (Normal, DoS, Web) from training folders."""
    dfs = []

    # Normal + DoS
    for folder_name, label in [("Normal", "Normal"), ("DoS", "DoS")]:
        folder_path = BASE_DIR / folder_name
        if (folder_path / "csv").exists():
            folder_path = folder_path / "csv"

        for csv_file in folder_path.rglob("*.csv"):
            print(f"[TRAIN LOAD] {label} from {csv_file}")
            df = pd.read_csv(csv_file)
            df["Label"] = label
            dfs.append(df)

    # UPDATED — Web now includes XSS
    web_base = BASE_DIR / "Web"
    for sub in WEB_SUBFOLDERS:
        sub_path = web_base / sub
        if (sub_path / "CSV").exists():
            sub_path = sub_path / "CSV"

        for csv_file in sub_path.rglob("*.csv"):
            print(f"[TRAIN LOAD] Web from {csv_file}")
            df = pd.read_csv(csv_file)
            df["Label"] = "Web"
            dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


def load_test_subset() -> pd.DataFrame:
    """
    Load TEST data for classes:
    - Normal
    - Web (command-injection, sql, xss)
    - DoS (slowhttp, tcp, stomp)
    """
    test_dir = BASE_DIR / "TEST"
    dfs = []

    # UPDATED — Added XSS mapping
    mapping = {
        "normal": "Normal",
        "command-injection": "Web",
        "sql": "Web",
        "xss": "Web",
        "slowhttp": "DoS",
        "tcp": "DoS",
        # "stomp": "DoS",
    }

    # Support TEST/CSV also
    for csv_file in test_dir.rglob("*.csv"):
        fname = csv_file.stem.lower()

        label = None
        for key, lab in mapping.items():
            if key in fname:
                label = lab
                break

        if label is None:
            print(f"[TEST SKIP] {csv_file} (not mapped)")
            continue

        print(f"[TEST LOAD] {label} from {csv_file}")
        df = pd.read_csv(csv_file)
        df["Label"] = label
        dfs.append(df)

    if not dfs:
        raise RuntimeError("No TEST CSV files loaded – check TEST folder mapping.")

    return pd.concat(dfs, ignore_index=True)


def clean_numeric(df: pd.DataFrame) -> pd.DataFrame:
    drop_cols = [
        "src_ip", "dst_ip", "src_port", "dst_port",
        "protocol", "timestamp", "flow_id", "Flow ID"
    ]

    for col in drop_cols:
        if col in df.columns:
            df = df.drop(columns=[col])

    label_col = "Label"
    label_series = df[label_col].copy()

    df_num = df.drop(columns=[label_col])
    df_num = df_num.select_dtypes(include=[np.number])

    df_num = df_num.replace([np.inf, -np.inf], np.nan)
    df_num = df_num.dropna()

    label_series = label_series.loc[df_num.index]

    df_clean = df_num.copy()
    df_clean[label_col] = label_series
    return df_clean


def fit_global_preprocessors(df):
    le = LabelEncoder()
    y = le.fit_transform(df["Label"])
    X = df.drop(columns=["Label"]).values

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    feature_cols = [f"f{i}" for i in range(X_scaled.shape[1])]
    df_scaled = pd.DataFrame(X_scaled, columns=feature_cols, index=df.index)
    df_scaled["Label"] = y

    joblib.dump(le, PREP_DIR / "label_encoder.pkl")
    joblib.dump(scaler, PREP_DIR / "scaler.pkl")
    print(f"[SAVE] label_encoder.pkl and scaler.pkl saved.")

    return df_scaled, le, scaler, feature_cols


def apply_preprocessors(df, le, scaler, feature_cols):
    y = le.transform(df["Label"])
    X_scaled = scaler.transform(df.drop(columns=["Label"]).values)

    df_scaled = pd.DataFrame(X_scaled, columns=feature_cols, index=df.index)
    df_scaled["Label"] = y
    return df_scaled


# ==============================
# BUILD SPLITS
# ==============================
def build_centralized(df_scaled):
    out = PREP_DIR / "centralized.csv"
    df_scaled.to_csv(out, index=False)
    print(f"[SAVE] Centralized -> {out}")


def build_iid_clients(df_scaled):
    X = df_scaled.drop(columns=["Label"]).values
    y = df_scaled["Label"].values

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    for i, (_, idx) in enumerate(skf.split(X, y), start=1):
        df_client = df_scaled.iloc[idx].reset_index(drop=True)
        out = PREP_DIR / f"iid_client{i}.csv"
        df_client.to_csv(out, index=False)
        print(f"[SAVE] IID client {i} -> {out}")


def load_noniid_client_raw(cid: str) -> pd.DataFrame:
    dfs = []

    for folder_name, label in [("Normal", "Normal"), ("DoS", "DoS")]:
        folder_path = BASE_DIR / folder_name
        if (folder_path / "csv").exists():
            folder_path = folder_path / "csv"

        for csv_file in folder_path.rglob("*.csv"):
            if f"Dataset-{cid}" not in csv_file.name:
                continue
            print(f"[NONIID LOAD] {label} client {cid} from {csv_file}")
            df = pd.read_csv(csv_file)
            df["Label"] = label
            dfs.append(df)

    web_base = BASE_DIR / "Web"
    for sub in WEB_SUBFOLDERS:
        sub_path = web_base / sub
        if (sub_path / "CSV").exists():
            sub_path = sub_path / "CSV"

        for csv_file in sub_path.rglob("*.csv"):
            if f"Dataset-{cid}" not in csv_file.name:
                continue
            print(f"[NONIID LOAD] Web client {cid} from {csv_file}")
            df = pd.read_csv(csv_file)
            df["Label"] = "Web"
            dfs.append(df)

    if not dfs:
        print(f"[WARN] Client {cid} empty")
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


def build_noniid_clients(le, scaler, feature_cols):
    for cid in CLIENT_IDS:
        df_raw = load_noniid_client_raw(cid)
        if df_raw.empty:
            continue

        df_clean = clean_numeric(df_raw)
        df_scaled = apply_preprocessors(df_clean, le, scaler, feature_cols)

        out = PREP_DIR / f"noniid_client{cid}.csv"
        df_scaled.to_csv(out, index=False)
        print(f"[SAVE] NonIID {cid} -> {out}")


def build_test(le, scaler, feature_cols):
    df_raw = load_test_subset()
    df_clean = clean_numeric(df_raw)
    df_scaled = apply_preprocessors(df_clean, le, scaler, feature_cols)

    out = PREP_DIR / "test.csv"
    df_scaled.to_csv(out, index=False)
    print(f"[SAVE] Test -> {out}")


# ==============================
# MAIN
# ==============================
def main():
    print(f"[INFO] BASE_DIR = {BASE_DIR}")

    df_raw = load_train_full()
    print(f"[INFO] Raw train: {df_raw.shape}")

    df_clean = clean_numeric(df_raw)
    print(f"[INFO] Clean train: {df_clean.shape}")

    df_scaled, le, scaler, feature_cols = fit_global_preprocessors(df_clean)

    build_centralized(df_scaled)
    build_iid_clients(df_scaled)
    build_noniid_clients(le, scaler, feature_cols)
    build_test(le, scaler, feature_cols)

    print("[DONE] Data preparation complete.")


if __name__ == "__main__":
    main()
