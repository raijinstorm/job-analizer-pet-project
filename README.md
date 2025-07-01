# Job Analyzer Pet Project

A simple job postings ETL pipeline and dashboard using Docker Compose.

## Features

* **ETL Fetcher** (`fetch_jobs.py`): Fetches jobs from Remotive API, transforms and loads into PostgreSQL.
* **Scheduler** (`scheduler.py`): Runs the ETL daily at 03:00.
* **Dashboard** (`app.py`): Streamlit app to explore and visualize job postings.
* **Database**: PostgreSQL 15 container with persistent data volume.

---

## Prerequisites

* Docker & Docker Compose installed on your machine.
* Git (to clone the repo).

---

## Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/raijinstorm/job-analizer-pet-project.git
   cd job-analyzer-pet-project
   ```

2. **Create a `.env` file** with your database settings:

   ```env
   PG_HOST=db
   PG_PORT=5432
   PG_DB=jobs
   PG_USER=admin
   PG_PASSWORD=admin
   ```

3. **Build and start all services**

   Before running this command ensure that your docker is running
   

   ```bash
   docker-compose up -d --build
   ```

   This will start three containers:

   * **db**: PostgreSQL database on host port `5432`.
   * **web**: Streamlit dashboard on host port `8501`.
   * **scheduler**: Scheduler that runs the ETL every day at 03:00.

---

## Accessing the Dashboard

Open your browser and go to:

```
http://localhost:8501
```

You can interact with filters, view charts, and download data.

---

## Viewing Logs

* **Database logs**:

  ```bash
  docker-compose logs -f db
  ```

* **Web dashboard logs**:

  ```bash
  docker-compose logs -f web
  ```

* **Scheduler logs**:

  ```bash
  docker-compose logs -f scheduler
  ```

---

## Stopping and Cleaning Up

* **Stop services**:

  ```bash
  docker-compose down
  ```

* **Remove volumes** (to wipe database data):

  ```bash
  docker-compose down -v
  ```

---

## Notes

* The scheduler writes logs via Python's `logging` module; check `/logs` if you mount a volume for persistence.
* To change the daily run time, edit `scheduler.py` (see `schedule.every().day.at(...)`).
* To modify the ETL parameters or search terms, update `scheduler.py` or call `fetch_jobs.py` directly.

---

Happy data analyzing! 👩‍💻👨‍💻
