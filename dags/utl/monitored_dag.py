# Copyright (c) PT Pintu Kemana Saja 2024 All Rights Reserved.

from datetime import datetime, timezone, timedelta
from prometheus_client import CollectorRegistry, Counter, Gauge, push_to_gateway
from airflow import DAG
import logging
from functools import partial
from typing import Optional, List, Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)



class DAGFactory:
    def _send_task_duration_metrics(self, team, dag_id, task_id, status, duration, run_id):
        registry = CollectorRegistry()
        task_duration_metrics = Gauge(
            name='airflow_task_duration_ms',
            documentation='Run Duration of a Task',
            labelnames=['team', 'task_id', 'status', 'dag_id', 'run_id'],
            registry=registry
        )
        task_duration_metrics.labels(
            team=team, task_id=task_id, status=status,
            dag_id=dag_id, run_id=run_id
        ).set(duration)
        try:
            push_to_gateway(
                self._pushgateway_url,
                dag_id,
                grouping_key={'task_id': task_id, 'dag_id': dag_id, 'status': status},
                registry=registry
            )
        except Exception as e:
            logger.error(f"Failed to push metrics for DAG {dag_id}, Task {task_id}: {e}")

    def _task_state_callback(self, context, team):
        required_keys = ['dag', 'task', 'ti', 'run_id', 'task_instance']
        if not all(key in context for key in required_keys):
            logger.error("Missing required keys in callback context")
            return

        task_instance = context['ti']
        if task_instance.start_date and task_instance.end_date:
            duration_ms = (task_instance.end_date - task_instance.start_date).total_seconds() * 1000
        else:
            duration_ms = (datetime.now(timezone.utc) - context['dag_run'].queued_at).total_seconds() * 1000

        self._send_task_duration_metrics(
            team=team,
            dag_id=context['dag'].dag_id,
            task_id=context['task'].task_id,
            status=context['task_instance'].state,
            duration=duration_ms,
            run_id=context['run_id']
        )

    def _send_sla_metrics(self, dag_id, task_id, team):
        registry = CollectorRegistry()
        dag_sla_metrics = Counter(
            name='airflow_sla_missed_count',
            documentation='SLA miss on DAG',
            labelnames=['task_id', 'dag_id', 'team'],
            registry=registry
        )
        dag_sla_metrics.labels(task_id=task_id, dag_id=dag_id, team=team).inc()
        try:
            push_to_gateway(
                self._pushgateway_url,
                dag_id,
                grouping_key={'task_id': task_id, 'dag_id': dag_id},
                registry=registry
            )
        except Exception as e:
            logger.error(f"Failed to push metrics for DAG {dag_id}, Task {task_id}: {e}")

    def _on_sla_miss(self, dag, task_list, blocking_task_list, slas, blocking_tis, team):
        if slas:
            self._send_sla_metrics(dag_id=slas[0].dag_id, task_id=slas[0].task_id, team=team)

    def create_monitored_dag(
        self,
        dag_id: str,
        team: str,
        dagrun_timeout: timedelta,
        schedule_interval: str,
        tags: List[str],
        owner: str,
        email: List[str],
        default_args: Dict[str, Any],
        catchup: bool = False,
        max_active_runs: int = 1,
        access_control: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ) -> DAG:
        try:
            cb = partial(self._task_state_callback, team=team)
            for callback_type in ['on_retry_callback', 'on_success_callback',
                                'on_failure_callback', 'on_skipped_callback']:
                default_args[callback_type] = [cb]

            defaults = {
                'depends_on_past': False,
                'start_date': datetime(2025, 1, 1),
                'retries': 1,
                'retry_delay': timedelta(seconds=5),
                'execution_timeout': dagrun_timeout or timedelta(hours=1),
                'owner': owner,
                'email': email,
            }
            defaults.update(default_args)

            return DAG(
                dag_id=dag_id,
                schedule_interval=schedule_interval,
                tags=tags,
                access_control=access_control,
                catchup=catchup,
                max_active_runs=max_active_runs,
                dagrun_timeout=dagrun_timeout,
                default_args=defaults,
                sla_miss_callback=partial(self._on_sla_miss, team=team),
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error creating DAG: {e}")
            raise


factory = DAGFactory()
