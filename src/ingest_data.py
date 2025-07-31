"""
A one-off script to populate the database with some sample data.

I put this together to get the project up and running with a realistic dataset.
It reads from the CSV files in the `data/archive/` directory, which I downloaded
from Kaggle, and loads the data into our PostgreSQL database.

It's designed to be run once during the initial setup.
"""
import os
import glob
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file (for the database connection)
load_dotenv()

def get_db_engine():
    """Creates a SQLAlchemy engine from the environment variables."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL is not set in the .env file!")
    
    # The 'echo=False' means it won't log every single SQL statement.
    # It can be noisy, but useful for debugging if something goes wrong.
    return create_engine(db_url, echo=False)

def create_tables(engine):
    """Creates the database tables based on the models."""
    # This is a bit of a hack to get the models loaded.
    # It relies on the fact that our models are defined in src/models.py
    from src.models import Base
    print("Creating database tables if they don't exist...")
    Base.metadata.create_all(engine)
    print("Tables created successfully (or already exist).")

def ingest_stock_data(engine):
    """
    Finds all the stock CSV files, processes them, and bulk-inserts them.
    """
    print("\nStarting stock data ingestion...")
    
    # The data is split into a bunch of CSVs, one for each stock.
    path = 'data/archive/stocks'
    all_files = glob.glob(os.path.join(path, "*.csv"))
    
    all_stocks_df = []
    total_files = len(all_files)

    for i, filename in enumerate(all_files):
        try:
            df = pd.read_csv(filename)
            # The ticker is in the filename, so we have to extract it.
            ticker = os.path.basename(filename).split('.')[0]
            df['ticker'] = ticker
            all_stocks_df.append(df)
            
            # A little progress indicator so we know it's not stuck.
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{total_files} files...")

        except Exception as e:
            print(f"  Could not process file {filename}. Error: {e}")

    print(f"  Processed a total of {total_files} files.")
    
    if not all_stocks_df:
        print("  No stock data found to ingest.")
        return

    # Combine all the individual dataframes into one big one.
    full_df = pd.concat(all_stocks_df, ignore_index=True)
    
    # Clean up the column names to match our database schema.
    full_df.rename(columns={
        'Date': 'date',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }, inplace=True)
    
    # Make sure the date is in the right format.
    full_df['date'] = pd.to_datetime(full_df['date'])
    
    print(f"  Concatenated all data into a single DataFrame with {len(full_df)} rows.")
    print("  Now writing to the 'historical_prices' table... (this might take a minute)")
    
    # Use `to_sql` for a fast bulk insert.
    full_df.to_sql('historical_prices', engine, if_exists='replace', index=False, chunksize=1000)
    
    print("  Stock data ingestion complete!")

def main():
    """The main function to run the whole ingestion process."""
    print("--- Starting Data Ingestion ---")
    engine = get_db_engine()
    create_tables(engine)
    ingest_stock_data(engine)
    print("\n--- Data Ingestion Finished ---")

if __name__ == "__main__":
    main()
