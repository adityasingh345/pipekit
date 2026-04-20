so maine abhi phase 4 pe hu , maine abhi tak @task decorator with lifecycle tracking banaya , DAG implment kiya , wave based execution order, 
artificat store kaya hota hai usko implement kaise karte hai.

-------------------------------------------------Next part is , state machine , jaise abhi pipekit print kar rah hai success and failure but usko ye cheez yaad nai rahega, that is why we use state machine, har run has , PENDING, RUNNING, SUCCESS, FAILED, RETRYING.

STATE MACHINE part is done (pending-> running -> success/failed)

-------------------------------------------------next part that i have to cover is retry mechanism.
if a task fails , try it again up to retries times. we want to wait a bit longer each time. this is called as exponential backoff.
attempt 1 fails -> wait 1s, attempt 2 fails -> wait 2s , attempt 3 fails -> wait 4s
then give up.
for now the wait formula is 2 ** atempt_number seconds.


----------------->>> right now we have to manually call http://dag.run(), but a real orchestrator should be able to run automatically-> like run this every day at 9am. for this we need scheduler
state machine for now is in memory before the scheduler we need persistent state with PostgresSQL.

if the process crashes, all run history gone, scheduler needs persistent state to know; 
1. did this pipeline already run today ?? 2. is it currently running, 3. dis the last run fail .


Why do you think we chose PostgreSQL specifically for state storage, instead of just writing to a file or keeping it in Redis?
 ANS-> 1. in postgresql , two workers can update state at the same time, postgress handles this with transactions and locks.
 2. QUERYING-> "show me all failed tasks in the last 7 days" is one sql line, whith the file we have to load the whole thing into memory and then manually search
 3. ACID guarantees -> if the server crashes mod-write, postgresql recovers cleanly.

 we will use sqlalchemy python orm to talk to postgress and alembic for migrations 


 ----------------> teh goal is to trigger and inspect pipelines from the terminal,
 @click.group() - make sthe command group. it is like the main entry point that holds sub-commands (run, status, logs)
 @click.command() - register the sub command under the group
 @click.argument("name") - a required positional argument.