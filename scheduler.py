import schedule 
import time
import subprocess

search_terms = ["python", "data", "devops", "machine learning"]

def run_all_searches():
    for i, term in enumerate(search_terms):
        print(f"Running for term: {term}")
        subprocess.run(["python", "fetch_jobs.py", "--search", term])
        time.sleep(60)
        
schedule.every().day.at("03:00").do(run_all_searches)

if __name__ == "__main__":
    # while True:
    #     schedule.run_pending()
    #     time.sleep(5)
    run_all_searches()