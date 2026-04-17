from pipekit.core.task import task

attempt_count = 0 

@task(retries=3)
def flaky():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise ValueError("not ready yet")
    return "finally worked"

result = flaky()
print(f"Result: {result}")