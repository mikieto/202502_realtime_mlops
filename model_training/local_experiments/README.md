# Local Experiments

This folder contains local notebook experiments and supporting files for building and evaluating a baseline and regression model (e.g., XGBoost) in a PoC (Proof of Concept) environment.

## Contents

- **`local_experiments.ipynb`**  
  Main Jupyter notebook where we:
  - Pull data from Spark Thrift Server
  - Perform data cleaning and profiling
  - Engineer basic features
  - Build a Baseline model
  - Build and compare a Regression model (XGBoost)

- **`data/`**  
  A directory that holds local CSV files or intermediate data, if needed.

- **`Dockerfile`**  
  A Dockerfile for spinning up a Jupyter notebook environment with all necessary dependencies (Spark, delta-spark, XGBoost, scikit-learn, etc.). 

- **`requirements.txt`**  
  Python library dependencies for local experiments. Typically includes:
  - `pyhive`
  - `pyspark` (if needed for local testing)
  - `xgboost`
  - `pandas`, `numpy`, `scikit-learn`
  - etc.

## How to Use

1. **Run Notebook Locally**  
   - Create and activate a virtual environment (optional).  
   - `pip install -r requirements.txt`  
   - Start Jupyter: `jupyter notebook`  
   - Open `local_experiments.ipynb` to explore or modify the data pipeline and models.

2. **Docker Approach**  
   - Build the Docker image:  
     ```bash
     docker build -t local_experiments_jupyter -f Dockerfile .
     ```
   - Run the container, mapping a port for Jupyter:
     ```bash
     docker run -p 8888:8888 local_experiments_jupyter
     ```
   - Access Jupyter via `http://localhost:8888` (depending on your Docker run output).

3. **Notebook Workflow**  
   - The notebook will connect to Spark Thrift Server (`spark-thrift`) to pull data.  
   - It then executes data cleaning, profiling (using `ydata_profiling`), feature engineering, building a Baseline model, and a Regression model.  
   - Finally, it compares metrics (MAE, RMSE, R^2) between Baseline and the Regression model.

## Notes

- This is primarily a demonstration of local experiments for real-time or batch data pipelines, focusing on quick iteration and model comparison.
- For production or more advanced usage, see the main architecture (e.g., Docker Compose, MLOps pipeline, etc.) outside this folder.
