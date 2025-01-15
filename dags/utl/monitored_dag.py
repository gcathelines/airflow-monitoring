# Copyright (c) PT Pintu Kemana Saja 2024 All Rights Reserved.

from datetime import timedelta, datetime, timezone

# from api_clients.pagerduty_client import PagerdutyClient
from prometheus_client import (CollectorRegistry, Counter, Gauge,
                               push_to_gateway)

from airflow import DAG
# import json
# from airflow.models import Variable
# from common.http_client import get_pushgateway_url
import logging
from functools import partial


# pagerduty_cred = json.loads(Variable.get("pagerduty_cred"))
logger = logging.getLogger()


class DAGFactory:
    """
        DAGFactory is a utility class to help create and monitor Airflow DAGs.
        It provides functionalities to automatically set up metrics collection
        (e.g., DAG/task duration, SLA misses) and integrates with Prometheus
        via Pushgateway. The class also integrates with PagerDuty for critical
        alerts.
    """
    pushgateway_url = None
    pagerduty_api_key = None
    _dag_duration_metrics = None
    _dag_sla_metrics = None

    def __init__(
        self,
        pushgateway_url='pushgateway:9091'
        # pushgateway_url=get_pushgateway_url(),
        # pagerduty_api_key=pagerduty_cred["data_escalation"]
    ):
        DAGFactory.pushgateway_url = pushgateway_url
        # DAGFactory.pagerduty_api_key = pagerduty_api_key
        DAGFactory._task_duration_metrics = Gauge(
            name='airflow_task_duration_ms',
            documentation='Run Duration of a DAG',
            labelnames=['team', 'task_id', 'status', 'dag_id', 'run_id'])
        DAGFactory._dag_sla_metrics = Counter(
            name='airflow_sla_missed_count',
            documentation='SLA miss on DAG',
            labelnames=['task_id', 'dag_id', 'team'])

    def create_monitored_dag(
                self,
                dag_id: str,
                team: str,
                dagrun_timeout: timedelta,
                schedule_interval: str,
                tags: list[str],
                access_control: dict,
                default_args: dict,
                catchup=False,
                max_active_runs=1,
                **kwargs
            ):
        if dag_id is None:
            raise ValueError("dag_id must be provided")
        if schedule_interval is None:
            raise ValueError("schedule_interval must be provided")
        if tags is None:
            raise ValueError("tags must be provided")
        if access_control is None:
            raise ValueError("access_control must be provided")
        if dagrun_timeout is None:
            raise ValueError("dagrun_timeout must be provided")

        if default_args is None:
            raise ValueError("default_args must be provided.")
        if default_args.get('owner', None) is None:
            raise ValueError("owner must be provided in default_args")
        if default_args.get('email', None) is None:
            raise ValueError("email must be provided in default_args")

        cb = default_args.get('on_retry_callback', None)
        if cb is None:
            cb = []
        elif not isinstance(cb, list):
            cb = [cb]
        cb.append(partial(DAGFactory._task_state_callback, team=team))
        default_args['on_retry_callback'] = cb

        cb = default_args.get('on_success_callback', None)
        if cb is None:
            cb = []
        elif not isinstance(cb, list):
            cb = [cb]
        cb.append(partial(DAGFactory._task_state_callback, team=team))
        default_args['on_success_callback'] = cb

        cb = default_args.get('on_failure_callback', None)
        if cb is None:
            cb = []
        elif not isinstance(cb, list):
            cb = [cb]
        cb.append(partial(DAGFactory._task_state_callback, team=team))
        default_args['on_failure_callback'] = cb

        cb = default_args.get('on_skipped_callback', None)
        if cb is None:
            cb = []
        elif not isinstance(cb, list):
            cb = [cb]
        cb.append(partial(DAGFactory._task_state_callback, team=team))
        default_args['on_skipped_callback'] = cb

        defaults = {
            'depends_on_past': False,
            'start_date': datetime(2025, 1, 1),
            'retries': 1,
            'retry_delay': timedelta(seconds=5),
            'execution_timeout': timedelta(hours=5)
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
            sla_miss_callback=partial(DAGFactory._on_sla_miss, team=team),
            **kwargs
        )

    @staticmethod
    def _send_sla_metrics(dag_id, task_id, team):
        registry = CollectorRegistry()
        DAGFactory._dag_sla_metrics.labels(
            task_id=task_id,
            dag_id=dag_id,
            team=team
        ).inc()
        registry.register(DAGFactory._dag_sla_metrics)
        try:
            push_to_gateway(
                DAGFactory.pushgateway_url,
                dag_id,
                grouping_key={'task_id': task_id, 'dag_id': dag_id},
                registry=registry
            )
        except Exception as e:
            logger.error(
                f"Failed to push metrics for DAG {dag_id}, "
                f"Task {task_id}: {e}"
            )

    @staticmethod
    def _on_sla_miss(dag, task_list, blocking_task_list, slas, blocking_tis, team):
        dag_id = slas[0].dag_id
        task_id = slas[0].task_id
        DAGFactory._send_sla_metrics(dag_id=dag_id, task_id=task_id, team=team)

    @staticmethod
    def _send_task_duration_metrics(
        team,
        dag_id,
        task_id,
        status,
        duration,
        run_id
    ):
        registry = CollectorRegistry()
        DAGFactory._task_duration_metrics.labels(
            team=team,
            task_id=task_id,
            status=status,
            dag_id=dag_id,
            run_id=run_id
        ).set(duration)
        registry.register(DAGFactory._task_duration_metrics)
        try:
            push_to_gateway(
                DAGFactory.pushgateway_url,
                dag_id,
                grouping_key={
                    'task_id': task_id,
                    'dag_id': dag_id,
                    'status': status,
                },
                registry=registry
            )
        except Exception as e:
            logger.error(
                f"Failed to push metrics for DAG {dag_id}, "
                f"Task {task_id}: {e}"
            )

    @staticmethod
    def _task_state_callback(context, team):
        required_keys = ['dag', 'task', 'ti', 'run_id', 'task_instance']
        for key in required_keys:
            if key not in context:
                logger.error(
                    f"Missing '{key}' in context for callback."
                )
                return
        dag_id = context['dag'].dag_id
        task_id = context['task'].task_id
        task_instance = context['ti']
        run_id = context['run_id']
        state = context['task_instance'].state
        duration_ms = -1
        if state:
            duration_ms = (
                datetime.now(timezone.utc) - context['dag_run'].queued_at
            ).total_seconds() * 1000
        else:
            duration_ms = (
                task_instance.end_date - task_instance.start_date
            ).total_seconds() * 1000
        DAGFactory._send_task_duration_metrics(
            team,
            dag_id,
            task_id,
            state,
            duration_ms,
            run_id
        )


factory = DAGFactory()
