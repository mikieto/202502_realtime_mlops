# streaming_config.py

import os
import yaml
from pathlib import Path

# Debug: Print current working directory
print("Current working directory:", os.getcwd())

try:
    # Load .env file explicitly from project root
    from dotenv import load_dotenv
    # Determine the project root (assuming this file is in project_root/spark_streaming/src/)
    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path = project_root / ".env"
    
    # Check if .env file exists
    if dotenv_path.is_file():
        print(f".env file found at: {dotenv_path}")
    else:
        print(f".env file NOT found at: {dotenv_path}")
    
    # Load .env file
    loaded = load_dotenv(dotenv_path=dotenv_path)
    print("Loaded .env file:", loaded)
    
    # Debug: Print the value of ENV and DEBUG from environment variables
    print("ENV variable:", os.getenv("ENV"))
    print("DEBUG variable:", os.getenv("DEBUG"))
except ImportError as e:
    print("dotenv module not found. Skipping .env loading.", e)

# Determine the environment (default to 'development')
env = os.getenv('ENV', 'development').lower()
print("Running in environment:", env)

# Choose the appropriate config file based on the environment
config_file = Path(__file__).parent / f"config_{'dev' if env=='development' else 'prod'}.yaml"
print("Using configuration file:", config_file)

if not config_file.is_file():
    raise FileNotFoundError(f"Configuration file not found: {config_file}")

# Load the YAML configuration file
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)
print("YAML configuration loaded:", config)

# Function to get configuration value with environment variable override
def get_config_value(key, default=None):
    # Return the value from OS environment if exists, otherwise from config file
    return os.getenv(key.upper(), config.get(key, default))

# Retrieve configuration values
KAFKA_BROKER = get_config_value('kafka_broker')
KAFKA_TOPIC = get_config_value('kafka_topic')
DELTA_LAKE_PATH = get_config_value('delta_lake_path')
CHECKPOINT_DIR = get_config_value('checkpoint_dir')

# Print configuration for debugging if DEBUG is set to true
if os.getenv('DEBUG', 'false').lower() == 'true':
    print("Configuration values:")
    print(f"KAFKA_BROKER: {KAFKA_BROKER}")
    print(f"KAFKA_TOPIC: {KAFKA_TOPIC}")
    print(f"DELTA_LAKE_PATH: {DELTA_LAKE_PATH}")
    print(f"CHECKPOINT_DIR: {CHECKPOINT_DIR}")

# Optionally, further processing can be added below...


