import abc
import json
import logging
import uuid

import shared.constants as constants

logger = logging.getLogger(__name__)

class BaseAdapter(abc.ABC):

    abc.abstractmethod
    async def _process_task():
        pass

    abc.abstractmethod
    async def _create_job_data():
        pass

    async def process_tasks(self):
        select_params = {"adapter": self.type, "state": "not_started", "version": self.version}
        task_info = self.db_client.select("tasks", select_params, selected="count(*) as count")
        task_count = task_info[0]["count"]
        logger.info(f"{self.type} - Tasks left to proces for {self.type}: {task_count}")
        tasks = self.get_tasks()
        while tasks:
            for task in tasks:
                task_count -= 1
                try:
                    logger.info(f"{self.type} - Processing task: {task['guid']}")
                    to_insert = await self._process_task(task["job_data"])
                    logger.debug(f"{self.type}: Datapoints to insert: {to_insert}")
                    self.db_client.bulk_create_if_not_exists("datapoints", to_insert)
                    self.set_task_state(task, "complete")
                    logger.info(f"{self.type} - Finished processing task: {task['guid']}, {task_count} left to go!")
                except Exception:
                    logger.warn(f"{self.type} - Failed to process task: {task['guid']}. Marking it as failed")
                    self.set_task_state(task, "failed")
            tasks = self.get_tasks()

    def get_tasks(self):
        select_params = {"adapter": self.type, "state": ["not_started", "failed"], "version": self.version}
        tasks = self.db_client.select("tasks", select_params, self.concurrent_tasks)

        for task in tasks:
            task["job_data"] = json.loads(task["job_data"])
        return tasks
    
    def set_task_state(self, task, state):
        self.db_client.update("tasks", {"guid": task["guid"]}, {"state": state})

    def generate_tasks(self):
        tasks = []
        cur_time = constants.start_time
        while cur_time < constants.end_time:
            for location, metadata in constants.data_by_location.items():
                job_data = json.dumps(self._create_job_data(location, metadata, cur_time), sort_keys=True)
                tasks.append({
                    "state": "not_started",
                    "job_data": job_data,
                    "version": self.version,
                    "guid": str(uuid.uuid5(uuid.NAMESPACE_X500, f"{job_data}-{self.type}-{self.version}")),
                    "adapter": self.type,
                })
            cur_time += self.granularity
        logger.info(f"{self.type} - Generating: {len(tasks)} tasks")
        self.db_client.bulk_create_if_not_exists("tasks", tasks)
