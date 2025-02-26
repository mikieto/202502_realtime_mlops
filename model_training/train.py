#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import mlflow
import mlflow.xgboost
from mlflow.tracking import MlflowClient

import pandas as pd
from pyhive import hive
import numpy as np

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def read_data_from_spark_thrift(
    host="spark-thrift",
    port=10000,
    username="spark",
    database="default",
    table="dbt_gold_eta_features"
):
    """Get a pandas DataFrame from Spark Thrift Server"""
    print("===== Reading data from Spark Thrift Server =====")
    conn = hive.Connection(
        host=host, 
        port=port, 
        username=username, 
        database=database
    )
    query = f"SELECT * FROM {table}"
    df = pd.read_sql(query, conn)
    conn.close()
    print("Shape of loaded data:", df.shape)
    return df


def data_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with null for final stops or negative travel_time."""
    print("===== Data Cleaning =====")
    
    # 1) Calculate max_seq
    max_seq = (
        df.groupby(["start_date", "trip_id"])["current_stop_sequence"]
        .max()
        .reset_index(name="max_seq")
    )
    df_merged = df.merge(max_seq, on=["start_date", "trip_id"], how="left")

    # 2) end-of-line null OR negative travel_time
    cond_end_null = (
        (df_merged["current_stop_sequence"] == df_merged["max_seq"]) &
        df_merged["next_arrival_time"].isnull()
    )
    cond_negative = (df_merged["travel_time_second"] < 0)
    cond_remove = cond_end_null | cond_negative

    before = len(df_merged)
    df_cleaned = df_merged[~cond_remove].copy()
    df_cleaned.drop(columns=["max_seq"], inplace=True)
    after = len(df_cleaned)
    print(f"Removed {before - after} rows (end_null or negative travel_time).")
    return df_cleaned


def remove_outliers_iqr(df: pd.DataFrame, col="travel_time_second") -> pd.DataFrame:
    """Remove outliers using IQR method"""
    print("===== Outlier Removal (IQR) =====")
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    before = len(df)
    df_no_outlier = df[
        (df[col] >= lower_bound) & (df[col] <= upper_bound)
    ].copy()
    after = len(df_no_outlier)
    print(f"Removed {before - after} outliers in {col}.")
    return df_no_outlier


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Add features like day_of_week and hour_of_day and convert datetime rows"""
    print("===== Feature Engineering =====")
    # Convert to datetime
    df["producer_timestamp"] = pd.to_datetime(df["producer_timestamp"])

    df["depature_delay_time_second"] = df["departure_delay_time_second"].astype(float)
    df["scheduled_travel_time_second"] = df["scheduled_travel_time_second"].astype(float)

    df["travel_time_second"] = df["travel_time_second"].astype(float)
    df["current_stop_sequence"] = df["current_stop_sequence"].astype(int)

    # Create day_of_week, hour_of_day
    df["day_of_week"] = df["arrival_time"].dt.weekday  # 0=Mon, 6=Sun
    df["hour_of_day"] = df["arrival_time"].dt.hour

    return df


def make_train_test(df: pd.DataFrame):
    """Encode trip_id and split train/test"""
    print("===== Split Train/Test =====")
    le = LabelEncoder()
    df["trip_id_encoded"] = le.fit_transform(df["trip_id"])

    feature_cols = ["trip_id_encoded", "current_stop_sequence", "day_of_week", "hour_of_day",
                "scheduled_travel_time_second", "departure_delay_time_second"]
    X = df[feature_cols].copy()
    y = df["travel_time_second"].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print("Train shape:", X_train.shape, "Test shape:", X_test.shape)
    return X_train, X_test, y_train, y_test


def run_baseline_model(X_train, y_train, X_test, y_test):
    """
    Baseline: 
      Record the average travel_time for each (trip_id, stop_seq, weekday, hour) group,
        and return the average if the key exists in the training data, otherwise the global average.
    """
    print("===== Baseline Model =====")
    
    # group by and get mean
    train_data = X_train.copy()
    train_data["travel_time_second"] = y_train

    group_cols = ["trip_id_encoded", "current_stop_sequence", "day_of_week", "hour_of_day"]
    baseline_means = train_data.groupby(group_cols)["travel_time_second"].mean()

    global_mean = train_data["travel_time_second"].mean()

    def baseline_predict(row):
        key = (
            row["trip_id_encoded"],
            row["current_stop_sequence"],
            row["day_of_week"],
            row["hour_of_day"]
        )
        if key in baseline_means:
            return baseline_means[key]
        else:
            return global_mean

    # apply
    preds = X_test.apply(baseline_predict, axis=1)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds, squared=False)
    r2 = r2_score(y_test, preds)

    print(f"MAE={mae:.3f}, RMSE={rmse:.3f}")
    return mae, rmse, r2


def run_xgboost(X_train, y_train, X_test, y_test, params=None):
    """Train & evaluate XGBoost """
    print("===== XGBoost Model =====")
    if params is None:
        params = {
            "random_state": 42,
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
        }
    model = XGBRegressor(**params)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds, squared=False)
    r2 = r2_score(y_test, preds)

    print(f"MAE={mae:.3f}, RMSE={rmse:.3f}, R^2={r2:.3f}")
    return model, mae, rmse, r2

def search_xgboost(X_train, y_train, X_test, y_test):
    # candidate hyperparameters for grid search (e.g.)
    max_depth_options = [3, 5, 7]
    learning_rate_options = [0.01, 0.05, 0.1]

    # initialize best values
    best_rmse = float("inf")
    best_params = None
    best_model = None

    for max_depth in max_depth_options:
        for lr in learning_rate_options:
            # A MLflow run for each parameter set
            with mlflow.start_run(run_name=f"XGBoost md={max_depth}, lr={lr}"):
                params = {
                    "random_state": 42,
                    "n_estimators": 100,
                    "max_depth": max_depth,
                    "learning_rate": lr,
                }
                mlflow.log_params(params)  # log hyperparameters

                model = XGBRegressor(**params)
                model.fit(X_train, y_train)
                preds = model.predict(X_test)

                mae = mean_absolute_error(y_test, preds)
                rmse = mean_squared_error(y_test, preds, squared=False)
                r2 = r2_score(y_test, preds)

                mlflow.log_metric("mae", mae)
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("r2", r2)

                # save the model
                mlflow.xgboost.log_model(model, artifact_path="model")

                # print the result
                print(f"Done: max_depth={max_depth}, lr={lr}, RMSE={rmse:.3f}, R^2={r2:.3f}")

                if rmse < best_rmse:
                    best_rmse = rmse
                    best_params = params
                    best_model = model

    return best_params, best_rmse, best_model


def main():
    # It is okay to use mlflow.set_tracking_uri("http://MLFLOW_HOST:5000") if you have a MLflow server

    # Step1: Read from Spark Thrift
    df = read_data_from_spark_thrift(
        host="spark-thrift",
        port=10000,
        username="spark",
        database="default",
        table="dbt_gold_eta_features"
    )

    # Step2: Cleaning data
    df = data_cleaning(df)

    # Step3: Remove outliers with IQR
    df = remove_outliers_iqr(df, col="travel_time_second")

    # Step4: Feature engineering
    df = feature_engineering(df)

    # Step5: train/test split
    X_train, X_test, y_train, y_test = make_train_test(df)

    # -----------------------------------------------------------------------
    # Log 2 experiments with MLflow: (1)Baseline, (2)XGBoost
    # -----------------------------------------------------------------------
    print("\n===== MLflow Logging =====")

    # ----------------------------------
    # 1) Baseline Model
    # ----------------------------------
    with mlflow.start_run(run_name="Baseline Model"):
        mae_base, rmse_base, r2_base = run_baseline_model(X_train, y_train, X_test, y_test)
        mlflow.log_param("model_type", "baseline")
        mlflow.log_metric("mae", mae_base)
        mlflow.log_metric("rmse", rmse_base)
        mlflow.log_metric("r2", r2_base)
        # no log_model for baseline, save it as pickle if needed.

    # ----------------------------------
    # 2) XGBoost Model
    # ----------------------------------
    with mlflow.start_run(run_name="XGBoost Model"):
        params = {
            "random_state": 42,
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
        }
        mlflow.log_params(params)

        model, mae_xgb, rmse_xgb, r2_xgb = run_xgboost(X_train, y_train, X_test, y_test, params=params)
        mlflow.log_metric("mae", mae_xgb)
        mlflow.log_metric("rmse", rmse_xgb)
        mlflow.log_metric("r2", r2_xgb)

        # Log XGBoost model to MLflow
        mlflow.xgboost.log_model(model, artifact_path="model")

    # ----------------------------------
    # 3) Hyperparameter Search
    # ----------------------------------
    print("\n===== Hyperparameter Search =====")
    best_params, best_rmse, best_model = search_xgboost(X_train, y_train, X_test, y_test)
    
    # ---------------------------
    # 4) Register the Best Model
    # ---------------------------
    # If you want to do it automatically in the same script:
    print(f"\nBest params from hyperparam search: {best_params} (RMSE={best_rmse:.3f})")

    with mlflow.start_run(run_name="Best Model from Search"):
        # we can re-calc final metrics or trust from best_model
        preds_best = best_model.predict(X_test)
        mae_best = mean_absolute_error(y_test, preds_best)
        rmse_best = mean_squared_error(y_test, preds_best, squared=False)
        r2_best = r2_score(y_test, preds_best)

        mlflow.log_params(best_params)
        mlflow.log_metric("mae", mae_best)
        mlflow.log_metric("rmse", rmse_best)
        mlflow.log_metric("r2", r2_best)

        model_name = os.getenv("MODEL_NAME", "MyXGBModel")

        # Now we log into the Model Registry
        model_info = mlflow.xgboost.log_model(
            best_model,
            artifact_path="model",
            registered_model_name=model_name
        )
    
        client = MlflowClient()

        versions = client.search_model_versions(f"name='{model_name}'")  
        latest_version = max(int(mv.version) for mv in versions)

        client.transition_model_version_stage(
            name=model_name,
            version=str(latest_version),
            stage="Production"
        )

    print("\nAll runs logged to MLflow. Check the UI to compare results.")
    print(f"Best hyperparams: {best_params} => RMSE={best_rmse:.3f}")

if __name__ == "__main__":
    main()
        
