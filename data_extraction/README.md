---

# Data Extraction

This directory contains the batch extraction job for the 202502_realtime_mlops project. The script extracts persistent data from Delta Lake, processes it (for example, converting Unix timestamps to datetime), and splits the data into training and test datasets (80% training and 20% test). The resulting datasets are saved as CSV files for downstream machine learning tasks.

---

## Overview

The data extraction job performs the following tasks:

1. **Read Data from Delta Lake:**  
   - Connects to the Delta Lake table where persistent data is stored.
   
2. **Data Processing:**  
   - Converts timestamp fields (e.g., from Unix seconds to datetime).
   - Performs any additional necessary data cleaning or formatting.
   
3. **Data Splitting:**  
   - Splits the processed data into training (80%) and testing (20%) sets.
   
4. **Save Output:**  
   - Writes the training and test datasets as CSV files to a specified output directory.

---

## Directory Structure

```
data_extraction/
├── extract_dataset.py         # Main extraction script
├── README.md                  # This file
└── [Optional additional files or configuration files]
```

---

## Prerequisites

Before running the extraction job, ensure that:

- **Python 3.8+** is installed.
- **Apache Spark** is installed (if your extraction uses PySpark).
- Required Python packages are installed (e.g., PySpark, pandas, scikit-learn). See the project's `requirements.txt` for details.
- A running Delta Lake table exists at the specified path (this could be a local path or cloud storage endpoint).
- Environment variables or configuration files (e.g., a `.env` file) define key settings such as:
  - The Delta Lake table location (e.g., `DELTA_PATH`).
  - The output directory for CSV files.
  - Any other necessary parameters.

---

## Installation

If you have not yet set up your Python environment, follow these steps:

1. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

   *(Ensure that `requirements.txt` lists all the dependencies such as PySpark, pandas, scikit-learn, etc.)*

---

## Configuration

Before running the script, check the following in `extract_dataset.py`:

- **DELTA_PATH:**  
  Set the correct path to your Delta Lake table.

- **Output Directory:**  
  Verify that the directory where the CSV files will be saved exists and has appropriate write permissions.

- **Timestamp Conversion & Data Splitting:**  
  Ensure that the timestamp conversion logic matches your data format and that the data splitting parameters (e.g., 80%/20%) are as desired.

---

## Usage

To run the data extraction job, execute the following command from the `data_extraction` directory:

```bash
python extract_dataset.py
```

The script will:

1. Read data from the Delta Lake table.
2. Convert timestamps and perform necessary data cleaning.
3. Split the data into training and testing datasets.
4. Save the resulting datasets as CSV files in the designated output directory.

---

## Troubleshooting

- **Data Not Found:**  
  Verify that the `DELTA_PATH` is correct and that the Delta Lake table exists at that location.

- **Timestamp Conversion Issues:**  
  Ensure the incoming timestamps are in the expected format (e.g., Unix seconds) and adjust the conversion logic if necessary.

- **Output File Errors:**  
  Check that the output directory exists and that the user running the script has sufficient write permissions.

- **Dependency Errors:**  
  Confirm that all required packages are installed. If not, review the `requirements.txt` file and install missing dependencies.

---

## Next Steps

Once the data extraction job completes and the CSV files are generated:

- Use the training dataset to build and train your machine learning models.
- Use the testing dataset to validate and evaluate your models.
- Integrate these datasets into further processing pipelines as needed for your project.

---

## Contact

If you have any questions or need further assistance, please refer to this document or contact the project maintainer.

---
