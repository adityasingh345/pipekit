so maine abhi phase 4 pe hu , maine abhi tak @task decorator with lifecycle tracking banaya , DAG implment kiya , wave based execution order, 
artificat store kaya hota hai usko implement kaise karte hai.

-------------------------------------------------Next part is , state machine , jaise abhi pipekit print kar rah hai success and failure but usko ye cheez yaad nai rahega, that is why we use state machine, har run has , PENDING, RUNNING, SUCCESS, FAILED, RETRYING.

STATE MACHINE part is done (pending-> running -> success/failed)

-------------------------------------------------next part that i have to cover is retry mechanism.
if a task fails , try it again up to retries times. we want to wait a bit longer each time. this is called as exponential backoff.
attempt 1 fails -> wait 1s, attempt 2 fails -> wait 2s , attempt 3 fails -> wait 4s
then give up.
for now the wait formula is 2 ** atempt_number seconds.
