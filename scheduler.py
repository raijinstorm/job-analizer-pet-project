import schedule 
import time
import subprocess
import logging 

logging.basicConfig(level=logging.INFO)

search_terms = ["python", "data", "devops", "machine learning"]

def run_all_searches():
    for i, term in enumerate(search_terms):
        logging.info(f"Running for term: {term}")
        subprocess.run(["python", "fetch_jobs.py", "--search", term])
        time.sleep(60)
        
schedule.every().day.at("03:00").do(run_all_searches)

if __name__ == "__main__":
    logging.info("Scheduler application had started")
    while True:
        schedule.run_pending()
        logging.info("Hm...Now I have to wait for an hour..")
        time.sleep(60*60)