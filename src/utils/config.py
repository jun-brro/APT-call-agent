import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent.parent.parent.absolute()

DATA_DIR = ROOT_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
VECTOR_DATA_DIR = DATA_DIR / 'vectors'

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'insurance_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

RAG_CONFIG = {
    'embedding_model': 'sentence-transformers/all-mpnet-base-v2',
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'vector_db_path': str(VECTOR_DATA_DIR / 'chroma_db')
}

ACTUARIAL_CONFIG = {
    'min_expense_rate': 0.0,
    'max_expense_rate': 1.0,
    'default_risk_free_rate': 0.03,
    'max_surrender_rate': 0.8,
    'surrender_period_months': 120
}

TOOL_CONFIG = {
    'model_id': 'watt-ai/watt-tool-8B',
    'max_new_tokens': 12800,
    'temperature': 0.7
} 