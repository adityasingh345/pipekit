# Pipekit 🚀

A simplified data pipeline orchestrator built from scratch in Python — similar to Apache Airflow but designed for deep understanding of distributed systems internals.

---

## What is Pipekit?

Pipekit lets you define tasks using simple Python decorators, express dependencies between them, and run them reliably — in the correct order, in parallel where possible, with retries, persistent state, and a REST API + CLI to control everything.

```python
@task
def extract():
    return fetch_from_api()

@task
def transform(data):
    return data.upper()

@task
def load(data):
    save_to_db(data)

transform.depends_on(extract)
load.depends_on(transform)

dag = Dag("etl_pipeline")
dag.add_task(extract)
dag.add_task(transform)
dag.add_task(load)
```

Then trigger it:

```bash
pipekit run etl_pipeline
```

---

## Architecture

```
CLI / REST API / Scheduler
         │
         ▼
     DAG Engine
  (Kahn's Algorithm)
         │
         ▼
  Task Queue (Redis)
         │
    ┌────┴────┐
    ▼         ▼
 Worker 1   Worker 2  ...
    │         │
    └────┬────┘
         ▼
   State Store (PostgreSQL)
```

| Layer | Technology | Role |
|---|---|---|
| API | FastAPI | Trigger and inspect pipelines over HTTP |
| CLI | Click | Terminal interface (`pipekit run`, `pipekit status`) |
| Scheduler | APScheduler | Cron + interval-based automatic triggering |
| DAG Engine | Python | Dependency resolution, wave-based execution order |
| Task Queue | Redis + Celery | Distribute tasks to workers, store results |
| Workers | Celery | Execute tasks in parallel across processes |
| State Store | PostgreSQL | Persist every task run's state and result |

---

## Features

- **`@task` decorator** — wrap any Python function as a pipeline task with retries and timeout support
- **DAG system** — define dependencies between tasks; pipekit figures out execution order automatically
- **Parallel execution** — tasks with no dependencies on each other run simultaneously across Celery workers
- **State machine** — every task transitions through `pending → running → success / failed`
- **Persistent state** — full audit trail in PostgreSQL; survives crashes and restarts
- **Retry with exponential backoff** — failed tasks retry with increasing wait times (2s, 4s, 8s...)
- **Artifact passing** — each task's output flows automatically as input to downstream tasks
- **REST API** — trigger pipelines and query status over HTTP
- **CLI tool** — `pipekit run` and `pipekit status` from the terminal
- **Scheduler** — run pipelines on a cron schedule or fixed interval automatically

---

## Quickstart

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis

### Installation

```bash
git clone https://github.com/yourusername/pipekit
cd pipekit
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Setup the database

```bash
psql -U postgres -c "CREATE DATABASE pipekit;"
```

### Start the services

**Terminal 1 — API server:**
```bash
uvicorn pipekit.api.routes:app --reload
```

**Terminal 2 — Celery worker:**
```bash
celery -A pipekit.worker.worker worker --loglevel=info
```

**Terminal 3 — Run a pipeline:**
```bash
pipekit run etl_pipeline
```

---

## CLI Usage

```bash
# Trigger a pipeline run
pipekit run <dag_name>

# Check the status of the last run
pipekit status <dag_name>
```

Example output:

```
[pipekit] Triggering pipeline: etl_pipeline
[pipekit] Status: completed
  extract: success
  transform: success
  load: success
```

---

## REST API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/pipelines/{dag_name}/run` | Trigger a pipeline run |
| `GET` | `/pipelines/{dag_name}/status` | Get last 10 task run states |

Interactive docs available at `http://localhost:8000/docs`

---

## Parallelism Demo

Define tasks that can run simultaneously:

```python
@task
def fetch_users(): ...

@task
def fetch_orders(): ...

@task
def fetch_products(): ...

@task
def merge(users, orders, products): ...

merge.depends_on(fetch_users, fetch_orders, fetch_products)
```

Each fetch task takes 2 seconds. Sequential execution = 6s. Pipekit dispatches all three to separate Celery workers simultaneously:

```
Total time: 2.04s  ✅
```

---

## Project Structure

```
pipekit/
├── pipekit/
│   ├── core/
│   │   ├── task.py        # @task decorator, retry logic, lifecycle tracking
│   │   ├── dag.py         # DAG class, Kahn's algorithm, wave execution
│   │   └── state.py       # TaskRun state machine
│   ├── scheduler/
│   │   └── scheduler.py   # APScheduler cron + interval triggers
│   ├── worker/
│   │   └── worker.py      # Celery worker, task registry
│   ├── api/
│   │   └── routes.py      # FastAPI endpoints
│   ├── db/
│   │   └── models.py      # SQLAlchemy models (PostgreSQL)
│   ├── tasks/
│   │   ├── etl_tasks.py   # Example ETL task definitions
│   │   └── parallel_tasks.py  # Example parallel task definitions
│   └── cli/
│       └── cli.py         # Click CLI (pipekit run, status)
├── examples/
│   ├── hello_pipeline.py
│   └── parallel_pipeline.py
├── tests/
└── pyproject.toml
```

---

## Key Concepts Implemented

**Kahn's Algorithm** — topological sort that produces a wave-based execution plan. Tasks at the same wave level have no dependencies on each other and run in parallel.

**State Machine** — every task run transitions through well-defined states. If the system crashes mid-run, the last persisted state tells you exactly where to resume.

**Exponential Backoff** — retry wait times grow exponentially (`2^attempt` seconds) to avoid hammering failing external services.

**Artifact Store** — task outputs are stored in-memory and passed as inputs to downstream tasks, enabling data flow through the pipeline without tight coupling.

**Distributed Workers** — Celery dispatches tasks to a Redis queue. Multiple worker processes consume from the queue simultaneously, achieving true parallelism across CPU cores or machines.

---

## Tech Stack

- **Python** — core language
- **FastAPI** — REST API
- **Click** — CLI
- **SQLAlchemy** — ORM for PostgreSQL
- **PostgreSQL** — persistent state storage
- **Redis** — message broker + result backend
- **Celery** — distributed task queue
- **APScheduler** — cron and interval scheduling

---

## What I Learned

Building Pipekit taught me that **reliability in distributed systems comes from state**. Without persistent state, a crash means losing everything. With it, you can observe, recover, and retry. This insight applies to every distributed system — not just pipeline orchestrators.

---

## Limitations & Future Work

- [ ] Dynamic DAG discovery — auto-register any `@task` without hardcoding
- [ ] Authentication on the REST API
- [ ] Distributed scheduler lock — prevent double-triggering with multiple scheduler instances
- [ ] Web UI — live DAG visualization and run history dashboard
- [ ] DAG versioning — track which version of a pipeline produced which results
- [ ] Durable artifact store — persist artifacts to PostgreSQL or S3 so they survive orchestrator restarts

---

## Inspired By

- [Apache Airflow](https://airflow.apache.org/)
- [Prefect](https://www.prefect.io/)
- [Dagster](https://dagster.io/)
