# RetailPulse – AI-Powered Customer Analytics & Demand Forecasting Platform

<div align="center">

![RetailPulse Banner](https://img.shields.io/badge/RetailPulse-AI%20Analytics-blue?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat-square&logo=streamlit)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-orange?style=flat-square)
![XGBoost](https://img.shields.io/badge/XGBoost-Churn-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

**End-to-End Data Science & Analytics Solution for Retail Demand Prediction & Customer Insights**

*Zidio Development — Data Science & Analytics Domain | March 2026*

</div>

---

## 🚀 Overview

**RetailPulse** is a production-grade AI analytics platform built for retail distribution networks. It ingests real transactional data and delivers:

| Capability | Description | Target Metric |
|---|---|---|
| 📈 Demand Forecasting | ARIMA + ETS ensemble, 30-day predictions | MAPE ≤ 12% |
| 👥 Customer Segmentation | RFM + K-Means clustering | 5 distinct segments |
| ⚠️ Churn Prediction | XGBoost + SHAP explainability | AUC-ROC ≥ 0.88 |
| 📦 Inventory Optimization | EOQ + Safety Stock + Reorder Point | Reduce stockouts 30-50% |

---

## 📊 Dataset

Real-world data from a **Campa Cola distribution network** (South India):

| File | Records | Description |
|---|---|---|
| `final_updated_orderitems_combined.csv` | 8,803 | Order line items |
| `updated_Orders.csv` | 2,033 | Order headers |
| `retailers.csv` | 806 | Retailer master data |
| `Updated_Products.csv` | 43 | Product catalog |
| `Updated_Invoices.csv` | 2,033 | Invoice & payment data |
| `Updated_Payements.csv` | 2,521 | Payment transactions |
| `CancelledOrders.csv` | 199 | Cancellation records |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Data Processing | Pandas, NumPy, Scikit-learn |
| Forecasting | StatsForecast (AutoARIMA + AutoETS) |
| ML Models | XGBoost, SHAP |
| Dashboard | Streamlit + Plotly |
| Experiment Tracking | MLflow |
| Containerization | Docker |

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/RetailPulse.git
cd RetailPulse
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your data
Place the CSV files in `data/raw/`:
```
data/raw/
├── final_updated_orderitems_combined.csv
├── updated_Orders.csv
├── retailers.csv
├── Updated_Products.csv
├── Updated_Invoices.csv
├── Updated_Payements.csv
├── CancelledOrders.csv
└── CancelledOrderItems.csv
```

### 5. Run the pipeline
```bash
python pipeline.py
```

### 6. Launch the dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📁 Project Structure

```
RetailPulse/
├── data/
│   ├── raw/               # Source CSV files
│   └── processed/         # Pipeline outputs (parquet)
├── src/
│   ├── data/              # Ingestion & cleaning
│   ├── features/          # RFM & time-series engineering
│   ├── models/            # Forecasting, segmentation, churn
│   └── optimization/      # Inventory EOQ logic
├── dashboard/
│   ├── app.py             # Main Streamlit app
│   └── pages/             # 6 dashboard pages
├── notebooks/             # EDA & model notebooks
├── tests/                 # Validation scripts
├── pipeline.py            # End-to-end pipeline runner
├── requirements.txt
└── Dockerfile
```

---

## 🎯 Key Results

- **Demand Forecasting MAPE**: < 12% on held-out test set
- **Churn AUC-ROC**: ≥ 0.88
- **Customer Segments**: 5 actionable retailer personas (Champions, Loyal, At Risk, etc.)
- **Inventory**: Real-time EOQ recommendations with safety stock

---

## 🐳 Docker

```bash
docker build -t retailpulse .
docker run -p 8501:8501 retailpulse
```

---

## 📄 License

MIT License — Zidio Development 2026
