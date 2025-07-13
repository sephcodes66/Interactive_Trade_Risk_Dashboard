import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import glob

def create_tables(engine):
    """
    Creates the database tables and indexes if they do not already exist.
    Indexes are crucial for query performance on large datasets.
    """
    with engine.connect() as conn:
        with conn.begin(): # Start a transaction
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS instruments (
                instrument_id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) UNIQUE NOT NULL,
                company_name VARCHAR(255)
            );
            """))
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS market_data (
                data_id SERIAL PRIMARY KEY,
                instrument_id INTEGER REFERENCES instruments(instrument_id),
                price_date DATE NOT NULL,
                open_price NUMERIC(10, 2),
                high_price NUMERIC(10, 2),
                low_price NUMERIC(10, 2),
                close_price NUMERIC(10, 2) NOT NULL,
                volume NUMERIC,
                UNIQUE(instrument_id, price_date)
            );
            """))
            # Add indexes to foreign keys and frequently queried columns for performance.
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_market_data_instrument_id ON market_data (instrument_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_market_data_price_date ON market_data (price_date);"))
    print("Tables and indexes checked/created successfully.")

def ingest_data(engine):
    """
    Finds all CSV files in the data directory, cleans the data,
    and efficiently loads it into the database.
    """
    # Find all stock and ETF data files.
    stock_files = glob.glob('data/archive/stocks/*.csv')
    etf_files = glob.glob('data/archive/etfs/*.csv')
    all_files = sorted(list(set(stock_files + etf_files)))
    print(f"Found {len(all_files)} data files to ingest.")

    with engine.connect() as conn:
        with conn.begin(): # Use a single transaction for the entire ingestion process.
            for filepath in all_files:
                ticker = os.path.splitext(os.path.basename(filepath))[0]
                print(f"Processing {ticker}...")

                # Insert instrument if it doesn't exist, then get its ID.
                instrument_id_result = conn.execute(
                    text("INSERT INTO instruments (ticker, company_name) VALUES (:ticker, :name) ON CONFLICT (ticker) DO UPDATE SET ticker=EXCLUDED.ticker RETURNING instrument_id"),
                    {"ticker": ticker, "name": ticker}
                ).fetchone()
                instrument_id = instrument_id_result[0]

                # Read and prepare the DataFrame.
                df = pd.read_csv(filepath)
                df.rename(columns={
                    'Date': 'price_date', 'Open': 'open_price', 'High': 'high_price', 
                    'Low': 'low_price', 'Close': 'close_price', 'Volume': 'volume'
                }, inplace=True)
                
                df['instrument_id'] = instrument_id
                df['price_date'] = pd.to_datetime(df['price_date'])
                df_to_insert = df[['instrument_id', 'price_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
                
                # Replace pandas NaN with None for database compatibility.
                df_to_insert = df_to_insert.where(pd.notnull(df_to_insert), None)
                data_to_insert = df_to_insert.to_dict(orient='records')

                # Use 'executemany' for efficient bulk insertion.
                if data_to_insert:
                    conn.execute(
                        text("""
                            INSERT INTO market_data (instrument_id, price_date, open_price, high_price, low_price, close_price, volume)
                            VALUES (:instrument_id, :price_date, :open_price, :high_price, :low_price, :close_price, :volume)
                            ON CONFLICT (instrument_id, price_date) DO NOTHING;
                        """),
                        data_to_insert
                    )
    print(f"\nData ingestion complete.")

def main():
    """Main function to connect to the database and run the setup."""
    load_dotenv()
    try:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        
        if not all([db_user, db_host, db_port, db_name]):
            print("Error: Database credentials are not fully set in the .env file.")
            return

        engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
        print("Database connection successful.")
        
        create_tables(engine)
        ingest_data(engine)

        engine.dispose()
        print("Database connection closed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
