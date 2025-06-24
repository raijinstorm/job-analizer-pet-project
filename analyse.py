import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

def load_data():
    load_dotenv()

    DATABASE_URL = (
        f"postgresql+psycopg2://"
        f"{os.getenv('PG_USER')}:"
        f"{os.getenv('PG_PASSWORD')}@"
        f"{os.getenv('PG_HOST')}:"
        f"{os.getenv('PG_PORT')}/"
        f"{os.getenv('PG_DB')}"
    )

    engine = create_engine(DATABASE_URL)
    
    return pd.read_sql("SELECT * FROM postings", engine)

def main():
    df = load_data()
    print(df.head(20))
    
if __name__ == "__main__":
    main()

