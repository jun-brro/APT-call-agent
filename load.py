import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from src.core.data.loader import DataLoader
from src.mappings import (
    KOREAN_TO_ENGLISH_COLUMNS,
    KOREAN_TO_ENGLISH_VALUES,
    DATA_FILE_MAPPINGS
)

# Initialize data loader
loader = DataLoader()

# Load test data
loader.load_test_data()

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

print(f"Connecting to: postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def preprocess_dataframe(df):
    # Map column names from Korean to English
    df.columns = [KOREAN_TO_ENGLISH_COLUMNS.get(col, col) for col in df.columns]
    
    # Map values from Korean to English for specific columns
    for col in ['insurance_category', 'insurance_type']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: KOREAN_TO_ENGLISH_VALUES.get(str(x), x) if pd.notnull(x) and str(x).strip() != '' else x)
    
    # Convert numeric columns
    for col in df.columns:
        if any(num_col in col.lower() for num_col in ['claims', 'payment', 'contracts', 'premium']):
            try:
                df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
            except:
                pass
    
    return df

base_path = "data/"

for table_name, file_name in DATA_FILE_MAPPINGS.items():
    full_path = base_path + file_name
    print(f"\nProcessing {file_name}...")
    try:
        if os.path.exists(full_path):
            df = pd.read_csv(full_path, encoding='utf-8' if '국민건강보험공단' not in file_name else 'euc-kr')
            df = preprocess_dataframe(df)
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Successfully imported {file_name} to {table_name}")
            print(f"Unique values in insurance_category: {df['insurance_category'].unique() if 'insurance_category' in df.columns else 'N/A'}")
        else:
            print(f"File not found: {full_path}")
    except Exception as e:
        print(f"Error with {file_name}: {str(e)}")