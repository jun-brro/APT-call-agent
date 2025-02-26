#!/bin/bash
set -a
source .env
set +a

echo "=========================================================="
echo "============ Starting Insurance Analysis ================="
echo "=========================================================="

echo "Using database configuration:"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "Database: $DB_NAME"
echo "User: $DB_USER"

export PGDATA=$HOME/pgdata
pg_ctl -D $PGDATA stop -m immediate || true
rm -rf $PGDATA

# Initialize PostgreSQL
echo "Initializing PostgreSQL database cluster..."
initdb -D $PGDATA --auth=trust --username=postgres

# Configure PostgreSQL
echo "Configuring PostgreSQL..."
echo "listen_addresses = '*'" >> $PGDATA/postgresql.conf
echo "port = $DB_PORT" >> $PGDATA/postgresql.conf
echo "host    all    all    0.0.0.0/0    trust" >> $PGDATA/pg_hba.conf
echo "local   all    all                  trust" >> $PGDATA/pg_hba.conf

# Start PostgreSQL server
echo "Starting PostgreSQL server..."
pg_ctl -D $PGDATA -l $HOME/pglog start

# Wait for PostgreSQL to be ready
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt to connect to PostgreSQL..."
    if pg_isready -h $DB_HOST -p $DB_PORT; then
        echo "PostgreSQL is ready!"
        sleep 5
        break
    fi
    if [ $attempt -eq $max_attempts ]; then
        echo "Failed to connect to PostgreSQL after $max_attempts attempts"
        exit 1
    fi
    attempt=$((attempt + 1))
    sleep 2
done

# Create database and initialize schema
echo "Creating database and initializing schema..."
createdb -h $DB_HOST -p $DB_PORT -U postgres $DB_NAME || true
psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -f sql_setting/product_development_schema.sql

# Additional verification
echo "Verifying database connection..."
if ! psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
    echo "Error: Database connection verification failed"
    exit 1
fi

# Show database status
echo -e "\n=== Database Status and Analytics ==="
echo "1. Table Structure:"
psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -c "\dt"

echo -e "\n2. Insurance Business Overview:"
psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -c "
SELECT 
    year,
    COUNT(DISTINCT insurance_category) as product_count,
    SUM(total_contracts) as total_contracts,
    SUM(total_risk_premium) as total_premium,
    ROUND(AVG(total_risk_premium / total_contracts), 2) as avg_premium_per_contract
FROM quarterly_insurance_contracts
GROUP BY year
ORDER BY year DESC;"

# Verify database is still running
echo "Final database connection verification..."
if ! pg_isready -h $DB_HOST -p $DB_PORT; then
    echo "Error: Database is not running before application start"
    exit 1
fi

# Activate conda environment
echo -e "\n=== Starting Tool Call Experiment ==="
echo "Activating conda environment..."
source ~/.bashrc
conda activate insurance

# Add project root to PYTHONPATH
echo "Adding project root to PYTHONPATH..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the application
echo "Running the application..."
python process_prompts.py

# Cleanup: Stop PostgreSQL server
echo -e "\nStopping PostgreSQL server..."
pg_ctl -D $PGDATA stop -m immediate