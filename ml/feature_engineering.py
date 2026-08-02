import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "Time",
    "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8",
    "V9", "V10", "V11", "V12", "V13", "V14", "V15",
    "V16", "V17", "V18", "V19", "V20", "V21", "V22",
    "V23", "V24", "V25", "V26", "V27", "V28",
    "Amount",
    "Amount_Log",
    "Time_Hours",
    "Time_Sin",
    "Time_Cos",
    "Amount_ZScore",
    "Amount_Anomaly",
    "Time_Diff",
    "Rapid_Transaction",
]


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the exact 38 features used by the FraudShield X model.
    """

    df = df.copy()

    # -----------------------------
    # Amount transformation
    # -----------------------------

    df["Amount_Log"] = np.log1p(df["Amount"])

    # -----------------------------
    # Time features
    # -----------------------------

    SECONDS_PER_DAY = 86400

    df["Time_Hours"] = (
        (df["Time"] % SECONDS_PER_DAY) / 3600
    )

    df["Time_Sin"] = np.sin(
        2 * np.pi * df["Time_Hours"] / 24
    )

    df["Time_Cos"] = np.cos(
        2 * np.pi * df["Time_Hours"] / 24
    )

    # -----------------------------
    # Amount anomaly
    # -----------------------------

    amount_mean = df["Amount"].mean()
    amount_std = df["Amount"].std()

    if amount_std == 0:
        amount_std = 1

    df["Amount_ZScore"] = (
        (df["Amount"] - amount_mean) / amount_std
    )

    df["Amount_Anomaly"] = (
        df["Amount_ZScore"].abs() > 3
    ).astype(int)

    # -----------------------------
    # Transaction velocity
    # -----------------------------

    df = df.sort_values("Time").reset_index(drop=True)

    df["Time_Diff"] = (
        df["Time"].diff().fillna(0)
    )

    df["Rapid_Transaction"] = (
        (df["Time_Diff"] <= 10)
    ).astype(int)

    # -----------------------------
    # Final feature order
    # -----------------------------

    return df[FEATURE_COLUMNS]