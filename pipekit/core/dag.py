from collections import deque
from pipekit.core.state import TaskRun, TaskState

class Dag:
    def __init__(self, name):
        self.name = name 
        self.tasks = {}
    
    def add_task(self, task):
        self.tasks[task.name] = task
        return self
    
    def get_execution_order(self):
        degree = {task.name: 0 for task in self.tasks.values()}
        #it creates dictionary called degree where key = task.name and value = 0
        
        for task in self.tasks.values():
            for dep in task.dependencies:
                degree[task.name] += 1 
        # for every dependencies increase the count 
        
        # now we will find the task that are not dependent on any other task degree of that task = 0.
        
        queue = deque()
        
        for task_name, count in degree.items():
            if count == 0:
                queue.append(self.tasks[task_name])
        
        # now we will repeat take a task -> run it -> and then unlock others 
        
        stages = []
        
        while queue:
            stage = list(queue)
            stages.append(stage)
            
            next_queue = deque()
            
            for current in stage:
                for task in self.tasks.values():
                    if current in task.dependencies:
                        degree[task.name] -= 1
                        
                        if degree[task.name] == 0:
                            next_queue.append(task)
            
            queue = next_queue
        
        total_task = sum(len(stage) for stage in stages)
        if total_task != len(self.tasks):
            raise ValueError("cycle detected in DAG")

        return stages  
    
    def run(self):      
        # we will learn artifact store , what is artifact store,we cant just pass the python return vaue between the tasks. the data need to go somewhere both task can reach. that somewhere is called artifact store. it could be a database, a file, a redis
        
        stages = self.get_execution_order()
        artifact_store = {} # task name and  -> result 
        run_log = {} # task_name > TaskRun
        
        for i, stage in enumerate(stages):
            for task in stage:
                
                tr = TaskRun(task_name= task.name)
                run_log[task.name] = tr
                
                inputs = [artifact_store[dep.name] for dep in task.dependencies]
                
                tr.mark_running()
                try:
                    result = task(*inputs)
                    artifact_store[task.name] = result
                    tr.mark_success(result)
                except Exception as e:
                    tr.mark_failed(str(e))
                    print(f"{self.name} failed at task {task.name}")
                    return run_log # it will stop everything
        
        print(f"{self.name} completed")
        return run_log  