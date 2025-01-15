# import json
#
# from airflow.models import Variable
# from utl import monitored_dag
#
# pushgateway_config = {
#     'host': 'pushgateway',
#     'port': 9091
# }
# # pagerduty_cred = json.loads(Variable.get("pagerduty_cred"))
#
#
# def get_pushgateway_url():
#     return f"{pushgateway_config.get('host')}:{pushgateway_config.get('port')}"
#
#
# dag_factory = monitored_dag.DAGFactory(
#     pushgateway_url=get_pushgateway_url(),
#     pagerduty_api_key=None,
# )
