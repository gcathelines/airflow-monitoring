
import textwrap
import random
from datetime import datetime, timedelta


# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG


# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import statsd
from utl.http_client import HttpClient
from metrics import on_success_callback, on_retry_callback, on_failure_callback, on_sla_miss


def metrics(**kwargs):
    httpCl = HttpClient(context='random_user',base_url='https://randomuser.me/')
    httpCl.get(endpoint='api', kwargs=kwargs)

# TODO
# Create wrapper to make SLA, Team, etc as required params
# also include the callbacks automatically
with DAG(
    "tutorial",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        'sla': timedelta(seconds=5),
        # 'execution_timeout': timedelta(seconds=300),
        'team':'cfp',
        # 'on_failure_callback': on_failure_callback, # or list of functions
        # 'on_success_callback': on_success_callback, # or list of functions
        # 'on_retry_callback': on_retry_callback, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="A simple tutorial DAG",
    schedule=timedelta(seconds=30),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    sla_miss_callback= on_sla_miss, # or list of functions
) as dag:

    # t1, t2 and t3 are examples of tasks created by instantiating operators

    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )    

    random_number = random.randint(0, 1)

    cmd = f"sleep {random_number*60}"

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command=cmd,
        retries=3,
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


    dag.doc_md = __doc__  # providing that you have a docstring at the beginning of the DAG; OR
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
    """  +  f"exit {random_number}"
    )

    t3 = BashOperator(
        task_id="templated",
        depends_on_past=False,
        bash_command=templated_command,
    )

    t4 = PythonOperator(task_id="my_metrics", python_callable=metrics, dag=dag)



    t4 >> t1 >> [t2, t3]
