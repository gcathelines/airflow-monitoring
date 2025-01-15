from prometheus_client import (CollectorRegistry, Summary, Counter,
                               push_to_gateway)

_dag_duration_metrics = Summary(
    name='airflow_dag_duration',
    documentation='Run Duration of a DAG',
    labelnames=['instance','team','task_id','status'])

_dag_sla_metrics = Counter(
    name='airflow_sla_miss',
    documentation='SLA miss on DAG',
    labelnames=['task_id'])

def send_duration_metrics(team, dag_id, task_id, run_id, status, duration):
    registry = CollectorRegistry()
    _dag_duration_metrics.labels(team=team, task_id=task_id, status=status, instance=run_id).observe(duration)
    registry.register(_dag_duration_metrics)
    push_to_gateway('pushgateway:9091',dag_id,grouping_key={'team':team, 'task_id':task_id},registry=registry)


def send_sla_metrics(dag_id, task_id):
    registry = CollectorRegistry()
    _dag_sla_metrics.labels(task_id=task_id).inc()
    registry.register(_dag_sla_metrics)
    push_to_gateway('pushgateway:9091',dag_id,grouping_key={'task_id':task_id},registry=registry)

# TODO call pagerduty instead
def on_sla_miss(dag, task_list, blocking_task_list, slas, blocking_tis):
    dag_id = slas[0].dag_id
    task_id = slas[0].task_id
    send_sla_metrics(dag_id=dag_id, task_id=task_id)

def on_success_callback(context):
    print('asd sc cb')
    run_id = context['run_id']
    dag_id = context['dag'].dag_id
    task_id = context['task'].task_id
    task_instance = context['ti']
    team = context['dag'].default_args.get('team','data')
    
    duration_ms = (task_instance.end_date - task_instance.start_date).total_seconds() * 1000
    send_duration_metrics(team, dag_id, task_id, run_id, 'success', duration_ms)

def on_failure_callback(context):
    print('asd fl cb')

    run_id = context['run_id']
    dag_id = context['dag'].dag_id
    task_id = context['task'].task_id
    task_instance = context['ti']
    team = context['dag'].default_args.get('team','data')
    
    duration_ms = (task_instance.end_date - task_instance.start_date).total_seconds() * 1000
    send_duration_metrics(team,dag_id,task_id, run_id, 'failed',duration_ms)

def on_retry_callback(context):
    print('asd rt cb')

    run_id = context['run_id']
    dag_id = context['dag'].dag_id
    task_id = context['task'].task_id
    task_instance = context['ti']
    team = context['dag'].default_args.get('team','data')
    
    duration_ms = (task_instance.end_date - task_instance.start_date).total_seconds() * 1000
    send_duration_metrics(team,dag_id,task_id, run_id, 'retry',duration_ms)