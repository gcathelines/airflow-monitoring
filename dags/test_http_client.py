from utl.monitored_dag import factory
from utl.http_client import HttpClient
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

def metrics(**kwargs):
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

    print(res.status_code, res.json())


dag = factory.create_monitored_dag(dag=DAG(
    "testing_http_client",
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
    },
    description="Another simple tutorial DAG",
    schedule=timedelta(seconds=600),
    start_date=datetime(2021, 1, 1),
    catchup=False,
), sla=timedelta(seconds=30), team='cfp')
with dag:

    t1 = PythonOperator(task_id="my_metrics", python_callable=metrics)

    t2 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    t1 >> t2
