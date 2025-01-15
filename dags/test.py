from utl.monitored_dag import factory
# from utl.http_client import HttpClient
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import random
import textwrap
import logging
from airflow.exceptions import AirflowSkipException
from utl.monitored_dag import logger

try:
 raise AirflowSkipException("exception msg")
except Exception as e:
    logging.error("testing error")
    raise e

def metrics(context):
    logger.warning("testing warning")
    logging.info("testing info")
    # httpCl = HttpClient(
    #     context='random_user',
    #     base_url='https://randomuser.me/'
    # )
    # httpCl.get(endpoint='api', kwargs=kwargs)
    try:
        raise AirflowSkipException("exception msg")
    except AirflowSkipException as e:
        logging.error("testing error")
        raise e


def metrics2(context):
    logging.error("yaha ura")


dag = factory.create_monitored_dag(
    team='cfp',
    dag_id="another_tutorial",
    dagrun_timeout=timedelta(minutes=1),
    default_args={
        "sla": timedelta(minutes=1000),
        "owner": "airflow",
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "on_failure_callback": metrics,
        "on_success_callback": metrics,
        "on_retry_callback": metrics2,
        "on_skipped_callback": metrics2,
    },
    description="Another simple tutorial DAG",
    schedule_interval="*/20 * * * *",
    tags=["example"],
    access_control={"cfp": ["read", "write"]},
    start_date=datetime(2021, 1, 1),
    catchup=False,
)

with dag:
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    random_number = random.randint(0, 1)

    cmd = "sleep 0"

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command=cmd,
        retries=3
    )
    t1.doc_md = textwrap.dedent(
        """\
    #### Task Documentation
    You can document your task using the attributes `doc_md` (markdown),
    `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
    rendered in the UI's Task Instance Details page.
    ![img](https://imgs.xkcd.com/comics/fixing_problems.png)
    **Image Credit:** Randall Munroe, [XKCD](https://xkcd.com/license.html)
    """
    )

    dag.doc_md = __doc__  # providing that you have a docstring at the \
    # beginning of the DAG; OR
    dag.doc_md = """
    This is a documentation placed anywhere
    """  # otherwise, type it like this

    random_number = random.randint(0, 1)

    templated_command = textwrap.dedent(
        """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
    {% endfor %}
    """ + "exit 0"
    )

    t3 = BashOperator(
        task_id="templated",
        depends_on_past=False,
        bash_command=templated_command
    )

    t4 = PythonOperator(task_id="my_metrics", python_callable=metrics)
    # t5 = PythonOperator(task_id="my_metric_2s", python_callable=metrics2)

    t1 >> [t2, t3] >> t4
