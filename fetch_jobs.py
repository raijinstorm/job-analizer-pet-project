import requests
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from typing import Tuple, List, Dict, Any
import argparse

def connect_db() -> Tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor]:
    """
    Sets connection to a database.

    Returns:
        tuple : A tuple containing a connection to database and cursor to the connection.
    """

    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        database=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
    )
    cur = conn.cursor()
    #logging.info("DataBase connection is set\n")
    print("DataBase connection is set")
    return conn, cur

def fetch_data(search = "python", limit=10, category = None, timeout = 10) -> pd.DataFrame:
    "Fetches data from remotive.com into a dataframe"
    params = {}
    if search:
        params["search"] = search
    if limit:
        params["limit"] = limit
    if category:
        params["category"] = category
    
    url = "https://remotive.com/api/remote-jobs"
    
    try:
        responce = requests.get(url, params=params, timeout=timeout)
        responce.raise_for_status()
        print(f"Data for search ({search}) is fetched!")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    
    try:
        data = responce.json()
        if not data or "jobs" not in data:
            raise ValueError("No jobs found")
        
        jobs = []
        for j in data["jobs"]:
            jobs.append({ 
                "id":j.get("id"),
                "title":j.get("title"),
                "company_name": j.get("company_name"),
                "category": j.get("category"),
                "job_type": j.get("job_type"),
                "salary": j.get("salary"),
                "publication_date": j.get("publication_date"),
                "url" : j.get("url")
            })
            
    except ValueError as e:
        print(f"Error parsing json: {e}")
        return None
    
    return pd.DataFrame(jobs)
    
def transform(df: pd.DataFrame) -> pd.DataFrame:
    "Corrects datatypes and cleans dataframe"
    
    df["publication_date"] = pd.to_datetime(df["publication_date"].str[:11], errors="coerce")
    df = df.astype({col: "string" for col in df.select_dtypes(include="object").columns})
    df.salary = df["salary"].fillna("")
    df.dropna()
    print(f"Data is cleaned. The DF contains {len(df)} rows")
    return df

def load_into_db(df):
    "Loads data into a Postgres SQL database"
    conn, cur = connect_db()
      
    try:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS postings (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                company_name TEXT NOT NULL,
                job_type TEXT NOT NULL,
                salary TEXT NOT NULL,
                publication_date DATE,
                url TEXT NOT NULL
                )  
        """)
        
        for _, row in df.iterrows():
            cur.execute("""INSERT INTO postings (id, title, company_name, job_type, salary, publication_date, url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)  ON CONFLICT (id) DO NOTHING""", (row["id"], row["title"], row["company_name"], row["job_type"], \
                        row["salary"], row["publication_date"], row["url"]))
            
        conn.commit()
        print("Data is loaded into DB")
    except Exception as e:
        conn.rollback()
        print(f"Error loading into DB: {e}")
    finally:
        cur.close()
        conn.close()
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", required=True)
    args = parser.parse_args()
    
    df = fetch_data(search=args.search, timeout=1000, limit=1000)
    
    df = transform(df)
    
    load_into_db(df)
    
if __name__ == "__main__":
    main()