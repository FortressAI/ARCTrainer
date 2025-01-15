import json
import redis
from loguru import logger

class MetricsDashboard:
    def __init__(self, redis_host="localhost", redis_port=6379, redis_db=0):
        """
        Initializes the Metrics Dashboard with Redis integration.

        Args:
            redis_host (str): Redis host.
            redis_port (int): Redis port.
            redis_db (int): Redis database number.
        """
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        logger.info("MetricsDashboard initialized.")

    def get_task_metrics(self):
        """
        Fetch task performance metrics from Redis.

        Returns:
            dict: Task metrics including success rates and processing times.
        """
        try:
            keys = self.redis_client.keys("metrics:tasks:*")
            metrics = {}

            for key in keys:
                task_id = key.split(":")[-1]
                metrics[task_id] = json.loads(self.redis_client.get(key))

            logger.info(f"Fetched {len(metrics)} task metrics from Redis.")
            return metrics
        except Exception as e:
            logger.error(f"Error fetching task metrics: {e}")
            return {}

    def get_system_metrics(self):
        """
        Fetch system performance metrics from Redis.

        Returns:
            dict: System metrics including LLM latency and Redis query times.
        """
        try:
            keys = self.redis_client.keys("metrics:system:*")
            metrics = {}

            for key in keys:
                metric_name = key.split(":")[-1]
                metrics[metric_name] = float(self.redis_client.get(key))

            logger.info(f"Fetched {len(metrics)} system metrics from Redis.")
            return metrics
        except Exception as e:
            logger.error(f"Error fetching system metrics: {e}")
            return {}

    def log_task_metrics(self, task_id, metrics_data):
        """
        Logs task performance metrics into Redis.

        Args:
            task_id (str): ID of the task.
            metrics_data (dict): Metrics data to log.
        """
        try:
            key = f"metrics:tasks:{task_id}"
            self.redis_client.set(key, json.dumps(metrics_data))
            logger.info(f"Logged metrics for task {task_id}.")
        except Exception as e:
            logger.error(f"Error logging metrics for task {task_id}: {e}")

    def log_system_metrics(self, metric_name, value):
        """
        Logs system performance metrics into Redis.

        Args:
            metric_name (str): Name of the metric.
            value (float): Metric value to log.
        """
        try:
            key = f"metrics:system:{metric_name}"
            self.redis_client.set(key, value)
            logger.info(f"Logged system metric {metric_name}: {value}.")
        except Exception as e:
            logger.error(f"Error logging system metric {metric_name}: {e}")

if __name__ == "__main__":
    # Example usage
    dashboard = MetricsDashboard()

    # Log task metrics
    dashboard.log_task_metrics("example_task_id", {"success_rate": 0.95, "avg_time": 1.2})

    # Log system metrics
    dashboard.log_system_metrics("llm_latency", 0.45)

    # Fetch metrics
    task_metrics = dashboard.get_task_metrics()
    system_metrics = dashboard.get_system_metrics()

    print("Task Metrics:", task_metrics)
    print("System Metrics:", system_metrics)
