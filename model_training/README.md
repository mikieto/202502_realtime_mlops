## **model_training/README.md**

```markdown
# model_training

This directory holds **training scripts and related files**. We use **MLflow** to log experiments (Baseline vs. XGBoost, plus possible hyperparameter searches). Typically, you’ll connect to Spark Thrift Server to pull data from a prepared table (e.g., `dbt_gold_eta_features`).

---

## Contents

- **`train.py`**  
  The main training script which does:
  1. Connect to **Spark Thrift** (using `pyhive` or similar) and query the table (e.g. `dbt_gold_eta_features`).
  2. Clean and preprocess data (removing outliers, feature engineering).
  3. Split into train/test sets.
  4. Trains a **Baseline model** and **XGBoost** model.
  5. Logs metrics (MAE, RMSE, R²) and parameters to **MLflow**.
  6. Optionally does hyperparameter searching (multiple XGBoost runs).

- **`requirements.txt`**  
  Lists Python dependencies for training, e.g.:
  - `mlflow`
  - `xgboost`
  - `scikit-learn`
  - `pyhive`
  - etc.

- (Optional) **`local_experiments/`**  
  If you have Jupyter notebooks or local test scripts.

---

## How to Use

### 1. Build & Run via Docker Compose

In `docker-compose.yml`, you might have:

```yaml
trainer:
  build:
    context: .
    dockerfile: ./model_training/Dockerfile
  container_name: trainer
  depends_on:
    - mlflow
    - spark-thrift
  environment:
    - MLFLOW_TRACKING_URI=http://mlflow:5000
    - SPARK_THRIFT_SERVER=spark-thrift:10000
    # If using S3 artifact store in MLflow, set the credentials:
    - AWS_ACCESS_KEY_ID=admin
    - AWS_SECRET_ACCESS_KEY=admin123
    - MLFLOW_S3_ENDPOINT_URL=http://minio:9000
  networks:
    - spark-network
```

Then:

```bash
docker-compose up trainer
```

- This runs `python model_training/train.py` inside the container.
- The script fetches data from Spark Thrift → does data cleaning → logs runs to MLflow.

### 2. Check MLflow UI

Open:

```
http://localhost:5000
```

- Compare runs: Baseline vs. XGBoost vs. hyperparam search.
- Evaluate MAE / RMSE / R² to see which config is best.
- Inspect artifacts (model files, etc.).

---

## Flow Summary

1. **Data** is prepared in Spark Thrift (via `dbt` or other steps).
2. **`train.py`** queries that table, splits train/test, trains the models.
3. **MLflow** is used to track runs, metrics, artifacts.
4. Possibly see if your new model outperforms the baseline.

---

## Customization

- **`train.py`**:  
  - Update data cleaning logic or your own feature engineering steps.
  - Add or remove models (RandomForest, LightGBM, etc.).
  - Adjust the hyperparameter search in `search_xgboost(...)`.

- **`requirements.txt`**:  
  - If you add new libraries (lightgbm, catboost, etc.), list them here.

- **Docker**:  
  - If you have additional system-level dependencies, update `model_training/Dockerfile`.

---

## Tips

- Usually we do a synergy with `dbt` (transform data) → Spark Thrift → `train.py`.  
- After training, you can optionally proceed to **FastAPI** inference (PoC 2.6 step), or any other deployment approach.
