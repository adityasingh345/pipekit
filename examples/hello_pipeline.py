from pipekit.core.task import task
from pipekit.core.dag import Dag

@task
def extract():
    print("extracting raw data")
    return "raw_data"

@task
def transform(data):
    print(f"transforming data: {data}")
    return data.upper()

@task
def load(data):
    print(f"loading data: {data}")
    return f"saved({data})"

transform.depends_on(extract)
load.depends_on(transform)

dag = Dag("etl_pipeline")
dag.add_task(extract)
dag.add_task(transform)
dag.add_task(load)

run_log = dag.run()

print("\n--- Run Summary ---")
for name, tr in run_log.items():
    print(tr)