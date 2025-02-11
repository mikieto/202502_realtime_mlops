# test.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root directory
project_root = Path(os.getcwd())  # 現在のカレントディレクトリがプロジェクトルートである前提
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

print("JAVA_HOME:", os.getenv("JAVA_HOME"))
