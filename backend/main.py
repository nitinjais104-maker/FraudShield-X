
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "fraudshield_rf_model.joblib"
SCALER_PATH = BASE_DIR / "models" / "fraudshield_scaler.joblib"
THRESHOLD_PATH = BASE_DIR / "models" / "threshold.txt"

DB_PATH = BASE_DIR / "database" / "fraudshield.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

with open(THRESHOLD_PATH, "r") as file:
    THRESHOLD = float(file.read().strip())


# ============================================================
# FEATURE NAMES
# ============================================================

BASE_FEATURES = [
    "Time",
    "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8",
    "V9", "V10", "V11", "V12", "V13", "V14", "V15",
    "V16", "V17", "V18", "V19", "V20", "V21", "V22",
    "V23", "V24", "V25", "V26", "V27", "V28",
    "Amount"
]

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
    "Rapid_Transaction"
]


# ============================================================
# DATABASE
# ============================================================

def init_database():

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                amount REAL NOT NULL,

                transaction_time REAL NOT NULL,

                fraud_probability REAL NOT NULL,

                fraud_percentage REAL NOT NULL,

                prediction INTEGER NOT NULL,

                result TEXT NOT NULL,

                risk_level TEXT NOT NULL,

                message TEXT NOT NULL,

                created_at TEXT NOT NULL
            )
        """)

        conn.commit()


init_database()


# ============================================================
# SAVE PREDICTION
# ============================================================

def save_prediction(
    transaction,
    probability,
    prediction,
    result,
    risk_level,
    message
):

    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute(
            """
            INSERT INTO predictions (
                amount,
                transaction_time,
                fraud_probability,
                fraud_percentage,
                prediction,
                result,
                risk_level,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction.Amount,
                transaction.Time,
                probability,
                probability * 100,
                prediction,
                result,
                risk_level,
                message,
                created_at
            )
        )

        conn.commit()


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="FraudShield X API",
    description="AI-powered Credit Card Fraud Detection API",
    version="3.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class Transaction(BaseModel):

    Time: float

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

    Amount: float


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(transaction: Transaction) -> pd.DataFrame:

    data = transaction.model_dump()

    df = pd.DataFrame([data])


    # --------------------------------------------------------
    # Amount transformation
    # --------------------------------------------------------

    df["Amount_Log"] = np.log1p(df["Amount"])


    # --------------------------------------------------------
    # Time features
    # --------------------------------------------------------

    seconds_per_day = 86400

    df["Time_Hours"] = (
        (df["Time"] % seconds_per_day) / 3600
    )

    df["Time_Sin"] = np.sin(
        2 * np.pi * df["Time_Hours"] / 24
    )

    df["Time_Cos"] = np.cos(
        2 * np.pi * df["Time_Hours"] / 24
    )


    # --------------------------------------------------------
    # Amount anomaly
    # --------------------------------------------------------

    amount_mean = float(scaler.mean_[29])
    amount_std = float(scaler.scale_[29])

    if amount_std == 0:
        amount_std = 1

    df["Amount_ZScore"] = (
        (df["Amount"] - amount_mean) / amount_std
    )

    df["Amount_Anomaly"] = (
        df["Amount_ZScore"].abs() > 3
    ).astype(int)


    # --------------------------------------------------------
    # Transaction velocity
    # --------------------------------------------------------

    df["Time_Diff"] = 0.0

    df["Rapid_Transaction"] = 0


    # --------------------------------------------------------
    # Final feature order
    # --------------------------------------------------------

    return df[FEATURE_COLUMNS]


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "project": "FraudShield X",
        "status": "online",
        "model": "Random Forest",
        "features": int(model.n_features_in_),
        "threshold": THRESHOLD
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model": "Random Forest",
        "threshold": THRESHOLD
    }


# ============================================================
# MODEL INFO
# ============================================================

@app.get("/model-info")
def model_info():

    return {
        "model": "Random Forest",
        "features": int(model.n_features_in_),
        "threshold": THRESHOLD,
        "pr_auc": 0.854,
        "precision": 0.9437,
        "recall": 0.9533,
        "f1_score": 0.9484
    }


# ============================================================
# PREDICTION
# ============================================================

@app.post("/predict")
def predict(transaction: Transaction):

    # --------------------------------------------------------
    # Create exact 38 model features
    # --------------------------------------------------------

    features_df = create_features(transaction)


    # --------------------------------------------------------
    # Scale features
    # --------------------------------------------------------

    scaled_features = scaler.transform(features_df)


    # --------------------------------------------------------
    # Prediction probability
    # --------------------------------------------------------

    probability = float(
        model.predict_proba(scaled_features)[0][1]
    )


    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    prediction = int(
        probability >= THRESHOLD
    )


    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    if prediction == 1:

        result = "FRAUD"
        risk_level = "HIGH RISK"
        message = "Transaction appears suspicious"

    else:

        result = "GENUINE"

        if probability >= 0.30:

            risk_level = "REVIEW"
            message = "Transaction requires additional review"

        else:

            risk_level = "LOW RISK"
            message = "Transaction appears to be genuine"


    # --------------------------------------------------------
    # Save prediction to database
    # --------------------------------------------------------

    save_prediction(
        transaction=transaction,
        probability=probability,
        prediction=prediction,
        result=result,
        risk_level=risk_level,
        message=message
    )


    # --------------------------------------------------------
    # API response
    # --------------------------------------------------------

    return {

        "prediction": prediction,

        "result": result,

        "risk_level": risk_level,

        "message": message,

        "fraud_probability": round(
            probability,
            4
        ),

        "fraud_percentage": round(
            probability * 100,
            2
        ),

        "threshold": THRESHOLD
    }


# ============================================================
# PREDICTION HISTORY
# ============================================================

@app.get("/history")
def prediction_history(limit: int = 20):

    limit = max(
        1,
        min(limit, 100)
    )


    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT

                id,

                amount,

                transaction_time,

                fraud_probability,

                fraud_percentage,

                prediction,

                result,

                risk_level,

                message,

                created_at

            FROM predictions

            ORDER BY id DESC

            LIMIT ?
            """,
            (limit,)
        ).fetchall()


    return {

        "count": len(rows),

        "transactions": [
            dict(row)
            for row in rows
        ]
    }


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

@app.get("/dashboard")
def dashboard():

    with sqlite3.connect(DB_PATH) as conn:

        # Total transactions

        total = conn.execute(
            """
            SELECT COUNT(*)
            FROM predictions
            """
        ).fetchone()[0]


        # Fraud detected

        fraud = conn.execute(
            """
            SELECT COUNT(*)
            FROM predictions
            WHERE result = 'FRAUD'
            """
        ).fetchone()[0]


        # Manual review

        review = conn.execute(
            """
            SELECT COUNT(*)
            FROM predictions
            WHERE risk_level = 'REVIEW'
            """
        ).fetchone()[0]


        # Genuine / low risk

        genuine = conn.execute(
            """
            SELECT COUNT(*)
            FROM predictions
            WHERE risk_level = 'LOW RISK'
            """
        ).fetchone()[0]


        # Average fraud probability

        avg_probability = conn.execute(
            """
            SELECT AVG(fraud_probability)
            FROM predictions
            """
        ).fetchone()[0]


    return {

        "total_analyzed": total,

        "fraud_detected": fraud,

        "manual_review": review,

        "genuine": genuine,

        "average_fraud_probability": round(
            avg_probability or 0,
            4
        )
    }