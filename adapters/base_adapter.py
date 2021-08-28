import abc
import json

class BaseAdapter(abc.ABC):

    abc.abstractmethod
    async def process_tasks():
        pass

    abc.abstractmethod
    async def process_task():
        pass

    def get_tasks(self):
        select_params = {"adapter": self.type, "state": "not_started"}
        tasks = self.db_client.select("tasks", select_params, self.concurrent_tasks)
        for task in tasks:
            task["job_data"] = json.loads(task["job_data"])
        return tasks
    
    def mark_tasks_as_complete(self, tasks):
        for task in tasks:
            self.db_client.update("tasks", {"guid": task["guid"]}, {"state": "completed"})
