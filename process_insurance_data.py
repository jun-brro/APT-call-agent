import pandas as pd
import os
from typing import Dict, Any
import numpy as np
import psycopg2
from io import StringIO
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.getenv('BASE_DIR')

class InsuranceDataProcessor:
    """Example class for processing insurance data and loading it into PostgreSQL database.
    Note: This is a template. Replace the processing logic with your actual implementation.
    """
    def __init__(self):
        self.base_dir = BASE_DIR
        self.data_dir = os.path.join(self.base_dir, 'data')
        # TODO: Replace with your actual category mappings
        self.category_mapping = {
            'category_1': 'type_a',
            'category_2': 'type_b',
            'category_3': 'type_c'
        }
        self.db_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'insurance_db',
            'user': os.environ.get('DB_USER', 'postgres'),
            'password': os.environ.get('DB_PASSWORD')
        }
        
    def process_quarterly_contracts(self) -> pd.DataFrame:
        """Process quarterly insurance contract data.
        
        Returns:
            DataFrame with columns matching quarterly_insurance_contracts table
        """
        # TODO: Replace with your data processing logic
        df = pd.read_csv(os.path.join(self.data_dir, 'your_contracts_file.csv'))
        
        # Example column mapping - adjust according to your data
        df.columns = [
            'year', 'insurance_category',
            'q1_contracts', 'q1_premium',
            'q2_contracts', 'q2_premium',
            'q3_contracts', 'q3_premium',
            'q4_contracts', 'q4_premium',
            'total_contracts', 'total_premium'
        ]
        
        return df
        
    def process_quarterly_claims(self) -> pd.DataFrame:
        """Process quarterly insurance claims data.
        
        Returns:
            DataFrame with columns matching quarterly_insurance_claims table
        """
        # TODO: Replace with your data processing logic
        df = pd.read_csv(os.path.join(self.data_dir, 'your_claims_file.csv'))
        
        # Example column mapping - adjust according to your data
        df.columns = [
            'year', 'insurance_category',
            'q1_accident_count', 'q1_claims',
            'q2_accident_count', 'q2_claims',
            'q3_accident_count', 'q3_claims',
            'q4_accident_count', 'q4_claims',
            'total_accident_count', 'total_claims'
        ]
        
        return df
        
    def process_age_based_contracts(self) -> pd.DataFrame:
        """Process age-based contract data.
        
        Returns:
            DataFrame with columns matching insurance_contracts_by_age table
        """
        # TODO: Replace with your data processing logic
        df = pd.read_csv(os.path.join(self.data_dir, 'your_age_based_file.csv'))
        
        # Example of restructuring age-based data
        result_data = []
        age_groups = [
            ('0-10', 'under_10'),
            ('10-20', '10_20'),
            ('20-30', '20_30'),
            ('30-40', '30_40'),
            ('40-50', '40_50'),
            ('50-60', '50_60'),
            ('60+', 'over_60')
        ]
        
        # TODO: Implement your age group data processing logic
        
        return pd.DataFrame(result_data)

    def process_claims_by_period(self) -> pd.DataFrame:
        """Process insurance claims by period data
        
        Returns:
            DataFrame with processed claims data by period
        """
        # TODO: Implement your claims by period processing logic
        # Example structure:
        df = pd.read_csv(os.path.join(self.data_dir, 'your_claims_by_period_file.csv'))
        
        # TODO: Add your column mappings
        df.columns = [
            'year', 'insurance_category', 'sub_category',
            'within_1year_incidents', 'within_1year_claims',
            # ... Add other necessary columns
        ]
        
        # TODO: Add your data processing logic
        # Example:
        # - Convert numeric columns
        # - Map categories
        # - Handle missing values
        # - Validate data
        
        return df

    def process_claims_by_amount(self) -> pd.DataFrame:
        """Process insurance claims by amount data
        
        Returns:
            DataFrame with processed claims data by amount
        """
        # TODO: Implement your claims by amount processing logic
        # Example structure:
        df = pd.read_csv(os.path.join(self.data_dir, 'your_claims_by_amount_file.csv'))
        
        # TODO: Add your column mappings
        df.columns = [
            'year', 'insurance_category', 'sub_category',
            'under_10m_incidents', 'under_10m_claims',
            # ... Add other necessary columns
        ]
        
        # TODO: Add your data processing logic
        # Example:
        # - Convert numeric columns
        # - Map categories
        # - Handle missing values
        # - Validate data
        
        return df

    def process_health_insurance_premium(self) -> pd.DataFrame:
        """Process health insurance premium data
        
        Returns:
            DataFrame with processed health insurance premium data
        """
        # TODO: Implement your health insurance premium processing logic
        # Example structure:
        df = pd.read_csv(os.path.join(self.data_dir, 'your_health_insurance_file.csv'))
        
        # TODO: Add your data transformation logic
        result_data = []
        # Example transformation structure:
        for _, row in df.iterrows():
            region = row['region']
            type_name = row['type']
            
            # TODO: Add your monthly data extraction logic
            for month in range(1, 13):
                result_data.append({
                    'region': region,
                    'type': type_name,
                    'year': 2022,  # TODO: Make this dynamic
                    'month': month,
                    'premium': 0.0  # TODO: Add actual premium calculation
                })
        
        return pd.DataFrame(result_data)

    def save_to_db(self, df: pd.DataFrame, table_name: str):
        """Save DataFrame to PostgreSQL database table"""
        conn = psycopg2.connect(**self.db_params)
        cur = conn.cursor()
        
        try:
            output = StringIO()
            df.to_csv(output, sep='\t', header=False, index=False)
            output.seek(0)
            
            cur.copy_from(output, table_name, null='', columns=df.columns.tolist())
            conn.commit()
            print(f'Successfully loaded data into {table_name}')
            
        except Exception as e:
            conn.rollback()
            print(f'Error loading data into {table_name}: {str(e)}')
            
        finally:
            cur.close()
            conn.close()

def main():
    """Main function to demonstrate usage"""
    processor = InsuranceDataProcessor()
    
    # Initialize database schema
    conn = psycopg2.connect(**processor.db_params)
    cur = conn.cursor()
    
    try:
        # Execute SQL schema from example.sql
        with open(os.path.join(processor.base_dir, 'sql_setting/example.sql'), 'r') as f:
            cur.execute(f.read())
        conn.commit()
        print('Successfully initialized database schema')
    except Exception as e:
        conn.rollback()
        print(f'Error initializing schema: {str(e)}')
    finally:
        cur.close()
        conn.close()
    
    # TODO: Replace with your actual data processing calls
    # Example usage:
    contracts = processor.process_quarterly_contracts()
    processor.save_to_db(contracts, 'quarterly_insurance_contracts')
    
    claims = processor.process_quarterly_claims()
    processor.save_to_db(claims, 'quarterly_insurance_claims')
    
    age_based = processor.process_age_based_contracts()
    processor.save_to_db(age_based, 'insurance_contracts_by_age')

if __name__ == '__main__':
    main()