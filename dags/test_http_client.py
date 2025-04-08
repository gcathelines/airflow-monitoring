from utl.monitored_dag import factory
from utl.http_client import HttpClient
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import logging
from airflow.exceptions import AirflowSkipException
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

def cb(context):
    logger.debug('cbbbb')


def metrics(**kwargs):
    # raise AirflowSkipException("Skipping this task")    
    logger.info('info log1')
    logger.debug('debug logs1')
    logger.warning('warn log1')
    logger.error('error log1 ')

    cl = HttpClient(base_url="https://api.ebird.org/v2/data/obs/US-HI-007",
                    context="testing")

    res = cl.get(endpoint="recent/notable", headers={
        "x-ebirdapitoken": "vkooe929kss6"
    }, params={
        "detail": "full"
    })
    time.sleep(10)
    print(res.status_code, res.json())

dag = factory.create_monitored_dag(
    dag_id="testing_http_client",
    default_args={
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "sla": timedelta(milliseconds=1),
    },
    description="Another simple tutorial DAG",
    start_date=datetime(2021, 1, 1),
    catchup=False,
    team='cfp',
    owner="asd@asd.com",
    email=["asd@asd.com"],
    dagrun_timeout=timedelta(seconds=300),
    tags=["cfp"],
    max_active_runs=1,
    schedule_interval='*/1 * * * *',
    access_control={},
)
callbacks = dag.default_args['on_success_callback']
callbacks.append(cb)

with dag:

    t1 = PythonOperator(task_id="my_metrics", python_callable=metrics)
    t2 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    t1 >> t2
