# 🛡️ FraudShield X

### AI-Based Credit Card Fraud Detection System

FraudShield X is an AI-powered credit card fraud detection system that analyzes transaction behavior and predicts the likelihood of fraudulent activity in real time.

The system combines **machine learning, feature engineering, FastAPI, and a web-based frontend** to provide an end-to-end fraud detection pipeline.

---

## 🚀 Overview

FraudShield X uses a trained **Random Forest Classifier** to analyze transaction signals and generate a fraud probability.

The system evaluates:

* Transaction amount
* Transaction time
* V1–V28 behavioral transaction signals
* Engineered transaction features
* Amount anomalies
* Time-based patterns

The final model uses **38 input features** and applies a configurable **0.70 fraud probability threshold** for the final fraud decision.

---

## ✨ Key Features

* 🤖 Random Forest fraud detection model
* ⚡ Real-time transaction prediction
* 🔢 38-feature ML pipeline
* 🧠 Automated feature engineering
* 🔍 Fraud probability scoring
* 🚦 Low Risk / Manual Review / High Risk classification
* 🌐 FastAPI REST API
* 💻 Interactive web frontend
* 🟢 Genuine demo transaction
* 🟠 Review demo transaction
* 🔴 High-Risk Fraud demo transaction
* 📊 Model performance information
* ❤️ Health-check API
* 🔒 CORS-enabled frontend/backend integration

---

## 🧠 Machine Learning Pipeline

FraudShield X follows the following pipeline:

```text
Transaction Input
       │
       ▼
┌──────────────────────┐
│ Raw Transaction Data │
│ Time, Amount, V1-V28  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Feature Engineering  │
│                      │
│ Amount_Log           │
│ Time_Hours           │
│ Time_Sin             │
│ Time_Cos             │
│ Amount_ZScore        │
│ Amount_Anomaly       │
│ Time_Diff            │
│ Rapid_Transaction    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Feature Scaling      │
│ StandardScaler       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Random Forest Model  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Fraud Probability    │
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────┐
│ Risk Decision              │
│                            │
│ < 0.30  → LOW RISK         │
│ 0.30–0.69 → REVIEW          │
│ ≥ 0.70 → HIGH RISK/FRAUD   │
└────────────────────────────┘
```

---

## 📊 Model Information

| Metric          |                    Value |
| --------------- | -----------------------: |
| Model           | Random Forest Classifier |
| Input Features  |                       38 |
| PR-AUC          |                    0.854 |
| Precision       |                   0.9437 |
| Recall          |                   0.9533 |
| F1 Score        |                   0.9484 |
| Fraud Threshold |                     0.70 |

The threshold is stored in:

```text
models/threshold.txt
```

---

## 🔢 Feature Engineering

The system starts with the original transaction fields:

```text
Time
V1 – V28
Amount
```

Additional engineered features are generated before prediction:

```text
Amount_Log
Time_Hours
Time_Sin
Time_Cos
Amount_ZScore
Amount_Anomaly
Time_Diff
Rapid_Transaction
```

This produces the final **38-feature input** used by the trained model.

### Amount Transformation

The transaction amount is transformed using:

```text
log(1 + Amount)
```

### Time Features

Transaction time is converted into hours and represented using cyclical sine and cosine features.

### Amount Anomaly

An amount z-score is calculated using the training scaler statistics.

Transactions with an absolute z-score greater than 3 are marked as anomalous.

---

## 🚦 Risk Classification

FraudShield X uses the model's fraud probability to determine the transaction risk.

### 🟢 Low Risk

```text
Probability < 0.30
```

The transaction appears to be genuine.

### 🟠 Manual Review

```text
0.30 ≤ Probability < 0.70
```

The transaction requires additional review.

### 🔴 High Risk

```text
Probability ≥ 0.70
```

The transaction is considered suspicious and is classified as fraud by the configured decision threshold.

---

## 🌐 API

FraudShield X provides a FastAPI backend.

### Base URL

```text
http://127.0.0.1:8000
```

### Root Endpoint

```http
GET /
```

Returns basic project and model information.

### Health Endpoint

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "model": "Random Forest",
  "threshold": 0.7
}
```

### Model Information

```http
GET /model-info
```

Returns model configuration and evaluation metrics.

### Prediction

```http
POST /predict
```

The endpoint accepts:

```text
Time
V1 – V28
Amount
```

and returns:

```text
Prediction
Result
Risk Level
Message
Fraud Probability
Fraud Percentage
Threshold
```

---

## 📥 Example Prediction Response

```json
{
  "prediction": 1,
  "result": "FRAUD",
  "risk_level": "HIGH RISK",
  "message": "Transaction appears suspicious",
  "fraud_probability": 0.9849,
  "fraud_percentage": 98.49,
  "threshold": 0.7
}
```

---

## 🖥️ Frontend

The project includes an interactive web interface for analyzing transactions.

The frontend provides:

* Transaction amount input
* Transaction time input
* V1–V28 signal input
* Quick demo transactions
* Real-time prediction results
* Fraud probability visualization
* Risk classification
* Detection pipeline information
* Model performance information

### Demo Transactions

The frontend contains three quick demo options:

```text
🟢 Genuine
🟠 Review
🔴 High-Risk Fraud
```

These load predefined transaction examples into the analysis form.

---

## 🧪 Verified Demo

The High-Risk Fraud demo was tested using a real dataset transaction.

Example:

```text
Transaction Amount: ₹153.46
Transaction Time: 56624
Fraud Probability: 98.49%
Risk Level: HIGH RISK
```

The corresponding original dataset transaction was verified as:

```text
Class = 1
```

This demonstrates the complete flow:

```text
Dataset Transaction
        ↓
Frontend
        ↓
FastAPI
        ↓
Feature Engineering
        ↓
Scaler
        ↓
Random Forest
        ↓
Fraud Probability
        ↓
Risk Decision
```

---

## 📁 Project Structure

```text
FraudShield-X/
│
├── backend/
│   └── main.py
│
├── data/
│   └── raw/
│       └── creditcard.csv
│
├── database/
│   └── fraudshield.db
│
├── docs/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── ml/
│   ├── feature_engineering.py
│   └── notebooks/
│       └── 01_data_exploration.ipynb
│
├── models/
│   ├── fraudshield_rf_model.joblib
│   ├── fraudshield_scaler.joblib
│   └── threshold.txt
│
├── tests/
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Technologies Used

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

### Machine Learning

* Scikit-learn
* Random Forest
* NumPy
* Pandas
* Joblib

### Frontend

* HTML5
* CSS3
* JavaScript

### Development

* Visual Studio Code
* PowerShell
* Git
* GitHub

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FraudShield-X
```

### 2. Create Virtual Environment

Windows:

```powershell
python -m venv .venv
```

### 3. Activate Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## ▶️ Running the Backend

From the project root:

```powershell
python -m uvicorn backend.main:app --reload
```

The API will start at:

```text
http://127.0.0.1:8000
```

Verify the server:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected:

```text
status    model
------    -----
healthy   Random Forest
```

---

## ▶️ Running the Frontend

Open another PowerShell terminal:

```powershell
cd C:\Users\nitin\Desktop\FraudShield-X\frontend
```

Start a local web server:

```powershell
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

---

## 🔌 API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 🧪 Testing

### Python Syntax Check

```powershell
python -m py_compile backend\main.py
```

### Backend Health Check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### Model Information

```powershell
Invoke-RestMethod http://127.0.0.1:8000/model-info
```

---

## 🔐 Security Considerations

FraudShield X is a machine-learning demonstration and should not be treated as a production financial security system without additional security controls.

A production deployment should include:

* Authentication and authorization
* HTTPS
* Rate limiting
* Request validation
* Secure secrets management
* Logging and monitoring
* Model monitoring
* Data privacy controls
* Model drift detection
* Secure model storage
* Database security

---

## ⚠️ Dataset Notice

The raw credit-card transaction dataset is used for machine-learning development and experimentation.

The dataset is intentionally excluded from version control through `.gitignore`.

Users should obtain the dataset separately and place it at:

```text
data/raw/creditcard.csv
```

The project should only be used with datasets that the user has permission to access and redistribute.

---

## 🔮 Future Improvements

Potential future improvements include:

* 🔐 User authentication
* 📊 Fraud analytics dashboard
* 📈 Transaction history
* 🗄️ Persistent prediction database
* 🚨 Real-time fraud alerts
* 📧 Email/SMS fraud notifications
* 🌐 Cloud deployment
* 🧠 Model comparison
* 🔄 Automated model retraining
* 📉 Model drift monitoring
* 🔍 Explainable AI using SHAP
* 📱 Mobile-friendly interface
* 📊 Advanced fraud analytics
* 🔑 API authentication and rate limiting

---

## 🎯 Project Goals

FraudShield X was developed to demonstrate how machine learning can be integrated into a complete software application rather than being limited to a standalone notebook.

The project combines:

```text
Machine Learning
       +
Feature Engineering
       +
REST API
       +
Frontend
       +
Real-Time Prediction
```

---

## 👨‍💻 Author

**Nitin Jaiswal**

B.Tech – Computer Science & Engineering
Buddha Institute of Technology, Gorakhpur

---

## 📌 Project Status

```text
████████████████████████████████  COMPLETED
```

Core machine-learning detection, API integration, frontend analysis, demo transactions, and risk classification are implemented and tested.

---

## ⭐ Support

If you find this project useful for learning or experimentation, consider giving the repository a ⭐ on GitHub.

---

### FraudShield X

**AI-Based Credit Card Fraud Detection**

> Detect suspicious transactions before they become financial threats.
