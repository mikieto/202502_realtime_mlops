# Model Documentation

## 1. Model Development Requirements

### Purpose
Build a regression model to predict the next station's arrival time or stop duration. We will use data from one day to evaluate the prediction accuracy. The goal is to improve the predicted arrival time compared to the baseline (past averages) and support efficient operation management.

### Data Requirements
- **Vehicle Position Data**: Latitude, longitude, and speed data for vehicle positions.
- **Scheduled Arrival Time**: The scheduled arrival time from the timetable.
- **Actual Arrival Time**: The actual arrival time for calculating delay.
- **Time of Day**: Time information (e.g., morning, afternoon, evening).
- **Route Information**: Route ID (`route_id`).
- **Previous Station Stop Time**: Stop time at the previous station (`previous_station_stop_time`).

### Model Requirements
- **Model Type**: Regression model (e.g., Linear Regression, Random Forest, or XGBoost).
- **Target Variable**: Predicted next station's arrival time or stop duration.
- **Evaluation Metrics**:
  - **MAE** (Mean Absolute Error): The error between actual and predicted arrival times.
  - **RMSE** (Root Mean Squared Error): A squared error-based metric.
  - **Baseline Model**: Compare the performance with the baseline (past average).
- **Data Splitting**:
  - **Training Data**: Historical operational data to train the model.
  - **Test Data**: Recent operational data to test the model's accuracy.

### Model Flow
1. **Data Collection**: Collect vehicle position data, actual arrival times, and route data from Delta Lake.
2. **Preprocessing**: Handle missing values, perform feature engineering, and process categorical variables.
3. **Training**: Train the model using the processed data and evaluate its performance.
4. **Inference**: Use FastAPI to provide predicted results via an API.

---

## 2. Model Design

### Purpose
The goal is to design a regression model to predict the next station's arrival time or stop duration using vehicle position data, route information, and delay information from actual and scheduled arrival times.

### Input Features

| Feature Name                | Type        | Description                                          | Notes                               |
|-----------------------------|-------------|------------------------------------------------------|-------------------------------------|
| `route_id`                  | Categorical | Route ID (processed using One-Hot Encoding or Embedding) | Helps differentiate between routes |
| `previous_station_stop_time` | Numeric     | Stop time at the previous station                     | Affects the next station's prediction |
| `scheduled_arrival_time`    | Datetime    | Scheduled arrival time (from the timetable)           | Used as the baseline                |
| `actual_arrival_time`       | Datetime    | Actual arrival time                                  | Helps calculate the delay           |
| `arrival_delay`             | Numeric     | Arrival delay (actual - scheduled arrival time)       | Reflects the delay in the prediction |
| `time_of_day`               | Categorical | Time of day (morning, afternoon, evening, etc.)        | Affects stop times depending on time |
| `distance_to_next_station`  | Numeric     | Distance to the next station (calculated from latitude/longitude) | Affects next station's arrival time |
| `speed`                     | Numeric     | Current speed                                         | Affects delay and stop times        |

### Output (Target)
- **`predicted_arrival_time`**: Predicted arrival time for the next station (in seconds).

### Model Flow
1. **Data Collection**: Collect vehicle position data, actual and scheduled arrival times, and route data.
2. **Feature Engineering**: Select features, handle missing data, and process categorical variables.
3. **Model Selection**: Use a regression model (e.g., Linear Regression or Random Forest) to predict the arrival time.
4. **Evaluation**: Evaluate model accuracy using MAE and RMSE metrics.

---

## 3. Data Usage Requirements

### Data to be Used
- **Vehicle Position Data**: Latitude, longitude, speed, and time data for vehicle position.
- **Scheduled Arrival Time**: The scheduled arrival time from the timetable.
- **Actual Arrival Time**: The actual arrival time to calculate delays.
- **Time of Day**: Time information (e.g., morning, afternoon, evening) which may affect stop times.
- **Route Information**: Route ID (`route_id`).

### Data Preprocessing

#### Data Collection
- **Data Sources**: Vehicle position data, scheduled and actual arrival times, and route information from Delta Lake or CSV files.

#### Feature Engineering
- **Categorical Variables**: Process `route_id` and `time_of_day` using One-Hot Encoding or as categorical variables.
- **Distance Calculation**: Calculate the distance to the next station (`distance_to_next_station`) using the Haversine formula based on latitude and longitude.
- **Delay Calculation**: Calculate the arrival delay (`arrival_delay`) as the difference between actual and scheduled arrival times.
- **Handling Missing Values**: For missing data (e.g., `previous_station_stop_time`), use average stop time from previous stations as a fallback.

#### Data Normalization
- Normalize or standardize features like speed and distance to next station to ensure they are on the same scale.

### Model Input Preprocessing
- **Standardization**: Standardize numeric features like `speed` and `distance_to_next_station` to bring them to a similar scale.
- **Time of Day Extraction**: Extract time of day from `timestamp` and convert it into categories (e.g., morning, afternoon, evening).

### Data Flow
1. **Data Collection**: Collect the necessary data from each source (vehicle positions, arrival times, route info).
2. **Feature Engineering**: Generate features, handle missing values, and apply transformations to categorical variables.
3. **Model Training**: Train the model using the processed data.
4. **Evaluation**: Test the model's accuracy using the test dataset and evaluate its performance.

