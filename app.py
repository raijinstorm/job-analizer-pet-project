from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

app = Flask(__name__)

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

@app.route('/')
def index():
    df = load_data()
    top_locations = df['job_type'].value_counts().head(5).to_dict()
    return render_template('dashboard.html', locations=top_locations)

if __name__ == '__main__':
    app.run(debug=True)