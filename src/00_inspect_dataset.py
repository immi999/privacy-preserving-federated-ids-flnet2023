import os
from pathlib import Path

import pandas as pd


# ====== CONFIG – EDIT BASE_DIR IF NEEDED ======
BASE_DIR = Path(__file__).resolve().parents[1] / "data"

# Map folder names to label strings
CLASS_FOLDERS = {
    "Normal": "Normal",
    "DoS": "DoS",
    "Web": "Web",  # we will merge Command/SQL Injection into Web
}

WEB_SUBFOLDERS = ["Command Injection", "SQL Injection","XSS"]

CLIENT_IDS = ["1", "2", "3"]  # match Dataset-1.csv, Dataset-2.csv, Dataset-3.csv


def load_all_data() -> pd.DataFrame:
    all_dfs = []

    # Normal + DoS: assume CSVs are directly inside these folders or a `csv` subfolder
    for folder_name, label in [("Normal", "Normal"), ("DoS", "DoS")]:
        folder_path = BASE_DIR / folder_name
        # If your CSVs are in a subfolder, e.g. 'csv', modify here:
        if (folder_path / "csv").exists():
            folder_path = folder_path / "csv"

        for csv_file in folder_path.rglob("*.csv"):
            print(f"[LOAD] {label} from {csv_file}")
            df = pd.read_csv(csv_file)
            df["Label"] = label
            all_dfs.append(df)

    # Web: Command Injection + SQL Injection merged
    web_base = BASE_DIR / "Web"
    for sub in WEB_SUBFOLDERS:
        sub_path = web_base / sub
        for csv_file in sub_path.rglob("*.csv"):
            print(f"[LOAD] Web from {csv_file}")
            df = pd.read_csv(csv_file)
            df["Label"] = "Web"
            all_dfs.append(df)

    full_df = pd.concat(all_dfs, ignore_index=True)
    return full_df


def inspect_client_splits(df: pd.DataFrame):
    """Roughly see how many rows each client (Dataset-1/2/3) has."""
    client_counts = {cid: 0 for cid in CLIENT_IDS}
    client_class_counts = {cid: {} for cid in CLIENT_IDS}

    # We'll just look at filenames again by re-reading file list instead of mapping row-wise
    # Simpler: re-walk the folders and count rows per client+label.
    for folder_name, label in [("Normal", "Normal"), ("DoS", "DoS")]:
        folder_path = BASE_DIR / folder_name
        if (folder_path / "csv").exists():
            folder_path = folder_path / "csv"

        for csv_file in folder_path.rglob("*.csv"):
            fname = csv_file.name
            cid = None
            for cid_candidate in CLIENT_IDS:
                if f"Dataset-{cid_candidate}" in fname:
                    cid = cid_candidate
                    break
            if cid is None:
                continue

            df_temp = pd.read_csv(csv_file)
            n = len(df_temp)
            client_counts[cid] += n
            client_class_counts[cid][label] = client_class_counts[cid].get(label, 0) + n

    # Web classes
    web_base = BASE_DIR / "Web"
    for sub in WEB_SUBFOLDERS:
        sub_path = web_base / sub
        for csv_file in sub_path.rglob("*.csv"):
            fname = csv_file.name
            cid = None
            for cid_candidate in CLIENT_IDS:
                if f"Dataset-{cid_candidate}" in fname:
                    cid = cid_candidate
                    break
            if cid is None:
                continue

            df_temp = pd.read_csv(csv_file)
            n = len(df_temp)
            client_counts[cid] += n
            client_class_counts[cid]["Web"] = client_class_counts[cid].get("Web", 0) + n

    print("\n=== Client Total Row Counts ===")
    for cid, total in client_counts.items():
        print(f"Client {cid}: {total} rows")

    print("\n=== Client Class Distribution ===")
    for cid, counts in client_class_counts.items():
        print(f"\nClient {cid}:")
        for label, c in counts.items():
            print(f"  {label}: {c}")


def main():
    print(f"Using BASE_DIR = {BASE_DIR}")
    df = load_all_data()
    print("\n=== Global Dataset Info ===")
    print("Shape:", df.shape)
    print("Columns:", list(df.columns)[:15], "...")

    print("\nGlobal class distribution:")
    print(df["Label"].value_counts())

    print("\nNow inspecting client-level splits:")
    inspect_client_splits(df)


if __name__ == "__main__":
    main()
