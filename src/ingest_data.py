import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

import glob

def ingest_data(engine):
    """Ingest a larger set of stock and ETF data into the database, ensuring core portfolio tickers are included."""
    
    # Define the tickers essential for the app's default portfolio
    required_tickers = [
        'AAPL', 'MSFT', 'AMZN', 'TSLA', 'JPM', 'V', 'PFE', 'DIS', 'ACN', 'AGG'
    ]
    
    # Create full paths for the required tickers
    required_files = set()
    for ticker in required_tickers:
        stock_path = f'data/archive/stocks/{ticker}.csv'
        etf_path = f'data/archive/etfs/{ticker}.csv'
        if os.path.exists(stock_path):
            required_files.add(stock_path)
        elif os.path.exists(etf_path):
            required_files.add(etf_path)

    # Get a larger list of other files to supplement the data
    stock_files = sorted(glob.glob('data/archive/stocks/*.csv'))[:100]
    etf_files = sorted(glob.glob('data/archive/etfs/*.csv'))[:50]
    
    # Combine the lists and remove duplicates
    all_files = sorted(list(set(stock_files + etf_files) | required_files))

    print(f"Found {len(all_files)} unique data files to ingest.")
    print(f"Ensuring required tickers {required_tickers} are included.")

    with engine.connect() as conn:
        # Use a transaction to ensure data integrity
        with conn.begin():
            for filepath in all_files:
                ticker = os.path.splitext(os.path.basename(filepath))[0]

                print(f"Processing {ticker} from {filepath}...")

                # Insert instrument and get its ID
                instrument_id_result = conn.execute(
                    text("INSERT INTO instruments (ticker, company_name) VALUES (:ticker, :name) ON CONFLICT (ticker) DO UPDATE SET ticker=EXCLUDED.ticker RETURNING instrument_id"),
                    {"ticker": ticker, "name": ticker}
                ).fetchone()
                
                instrument_id = instrument_id_result[0]

                # Read CSV and prepare DataFrame
                df = pd.read_csv(filepath)
                df.rename(columns={
                    'Date': 'price_date', 
                    'Open': 'open_price', 
                    'High': 'high_price', 
                    'Low': 'low_price', 
                    'Close': 'close_price', 
                    'Volume': 'volume'
                }, inplace=True)
                
                df['instrument_id'] = instrument_id
                df['price_date'] = pd.to_datetime(df['price_date'])
                
                df_to_insert = df[['instrument_id', 'price_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
                
                # Replace pandas NaN with None for database compatibility
                df_to_insert = df_to_insert.where(pd.notnull(df_to_insert), None)

                # Convert dataframe to a list of dictionaries for bulk insertion
                data_to_insert = df_to_insert.to_dict(orient='records')

                # Use executemany for efficient bulk insertion
                if data_to_insert:
                    conn.execute(
                        text("""
                            INSERT INTO market_data (instrument_id, price_date, open_price, high_price, low_price, close_price, volume)
                            VALUES (:instrument_id, :price_date, :open_price, :high_price, :low_price, :close_price, :volume)
                            ON CONFLICT (instrument_id, price_date) DO NOTHING;
                        """),
                        data_to_insert
                    )
    
    print(f"\nData ingestion complete for all {len(all_files)} tickers.")


def create_tables(engine):
    """Create tables in the PostgreSQL database if they do not exist."""
    with engine.connect() as conn:
        # Start a transaction
        with conn.begin():
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
        # The transaction is committed here
    print("Tables checked/created successfully.")

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
            print("Please ensure DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, and DB_NAME are all set.")
            return

        # Using SQLAlchemy engine for better connection management and pandas integration
        engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

        print("Database connection successful.")
        
        # Ensure tables exist before ingesting data
        create_tables(engine)
        
        ingest_data(engine)

        engine.dispose()
        print("Database connection closed.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
