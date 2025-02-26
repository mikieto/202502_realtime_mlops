FROM ghcr.io/mlflow/mlflow

# Set working directory
WORKDIR /app

# Install necessary dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Expose the port
EXPOSE 5000

# Command to run the application
CMD ["mlflow", "ui", "--host", "0.0.0.0", "--port", "5000"]
