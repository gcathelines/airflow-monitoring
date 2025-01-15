from datetime import datetime, timedelta


# Base URL of the target server
BASE_URL = "http://100.109.132.8:8083"

# List of absolute paths to test
paths = [
    "/bin/flag.txt",
    "/boot/flag.txt",
    "/cdrom/flag.txt",
    "/dev/flag.txt",
    "/etc/flag.txt",
    "/home/flag.txt",
    "/lib/flag.txt",
    "/lost/flag.txt",
    "/media/flag.txt",
    "/mnt/flag.txt",
    "/opt/flag.txt",
    "/proc/flag.txt",
    "/root/flag.txt",
    "/run/flag.txt",
    "/sbin/flag.txt",
    "/snap/flag.txt",
    "/srv/flag.txt",
    "/tmp/flag.txt",
    "/usr/flag.txt",
    "/var/flag.txt",
    "/bin/root/flag.txt",
    "/boot/root/flag.txt",
    "/cdrom/root/flag.txt",
    "/dev/root/flag.txt",
    "/etc/root/flag.txt",
    "/home/root/flag.txt",
    "/lib/root/flag.txt",
    "/lost/root/flag.txt",
    "/media/root/flag.txt",
    "/mnt/root/flag.txt",
    "/opt/root/flag.txt",
    "/proc/root/flag.txt",
    "/root/root/flag.txt",
    "/run/root/flag.txt",
    "/sbin/root/flag.txt",
    "/snap/root/flag.txt",
    "/srv/root/flag.txt",
    "/tmp/root/flag.txt",
    "/usr/root/flag.txt",
    "/var/root/flag.txt",
    "/bin/lazarus/flag.txt",
    "/boot/lazarus/flag.txt",
    "/cdrom/lazarus/flag.txt",
    "/dev/lazarus/flag.txt",
    "/etc/lazarus/flag.txt",
    "/home/lazarus/flag.txt",
    "/lib/lazarus/flag.txt",
    "/lost/lazarus/flag.txt",
    "/media/lazarus/flag.txt",
    "/mnt/lazarus/flag.txt",
    "/opt/lazarus/flag.txt",
    "/proc/lazarus/flag.txt",
    "/root/lazarus/flag.txt",
    "/run/lazarus/flag.txt",
    "/sbin/lazarus/flag.txt",
    "/snap/lazarus/flag.txt",
    "/srv/lazarus/flag.txt",
    "/tmp/lazarus/flag.txt",
    "/usr/lazarus/flag.txt",
    "/var/lazarus/flag.txt",
    "/bin/travel/flag.txt",
    "/boot/travel/flag.txt",
    "/cdrom/travel/flag.txt",
    "/dev/travel/flag.txt",
    "/etc/travel/flag.txt",
    "/home/travel/flag.txt",
    "/lib/travel/flag.txt",
    "/lost/travel/flag.txt",
    "/media/travel/flag.txt",
    "/mnt/travel/flag.txt",
    "/opt/travel/flag.txt",
    "/proc/travel/flag.txt",
    "/root/travel/flag.txt",
    "/run/travel/flag.txt",
    "/sbin/travel/flag.txt",
    "/snap/travel/flag.txt",
    "/srv/travel/flag.txt",
    "/tmp/travel/flag.txt",
    "/usr/travel/flag.txt",
    "/var/travel/flag.txt",
]

# HTTP methods to test
methods = ["GET", "OPTIONS", "TRACE", "PROPFIND"]

# Headers to test
test_headers = [
    {},
    {"Referer": "/root/flag.txt"},
    {"Range": "bytes=0-1"}
]

# Function to test paths
def test_paths():
    results = []
    for path in paths:
        url = BASE_URL + path
        for method in methods:
            for headers in test_headers:
                try:
                    response = requests.request(method, url, headers=headers, allow_redirects=False)
                    result = {
                        "method": method,
                        "path": path,
                        "headers": headers,
                        "status_code": response.status_code,
                        "response": response.text[:200]  # Limit response text for readability
                    }
                    results.append(result)
                    print(f"Tested {method} {url} with headers {headers} -> {response.status_code}")
                except Exception as e:
                    print(f"Error testing {method} {url} with headers {headers}: {e}")
    return results

# Run the tests
if __name__ == "__main__":
    results = test_paths()
    # Save results to a file for later analysis
    with open("path_test_results.txt", "w") as f:
        for result in results:
            f.write(f"{result}\n")
    print("Testing completed. Results saved to path_test_results.txt.")


# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# logging.basicConfig(
#     format='%(asctime)s %(levelname)s %(filename)s:%(lineno)-8s %(message)s',
#     level=logging.INFO,
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

# logger.error("asd formatted")

# from http_client import HttpClient, TLSAdapter
# from prometheus_client import (CollectorRegistry, Summary, Gauge,
#                                push_to_gateway)
# import logging
# import time
# import re

# cl = HttpClient(base_url="https://tls-v1-2.badssl.com/",
#                 context="testing",
#                 adapter={
#                     "https://": TLSAdapter(tls_version="TLSv1.2")
#                 })

# res = cl.get(endpoint="", headers={
#     "x-ebirdapitoken": "vkooe929kss6"
# }, params={
#     "detail": "full"
# })


# def sanitize_endpoint(endpoint: str):
#     uuid_pattern = r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}'
#     sanitized_string = re.sub(uuid_pattern, 'id', endpoint)
#     return sanitized_string

# # Create a registry for the metrics

# # Define the Gauge for HTTP request latency (in seconds)

# http_api_request_latency = Summary(
#     'aaa',  # Metric name (make sure it fits with your convention)
#     'HTTP API request latency in milliseconds',
#     labelnames=['endpoint', 'status_code', 'method',
#                 # 'timestamp'
#                 ],
# )


# # Function to record latency using Gauge and push to PushGateway
# def record_latency(endpoint, status_code, method, duration_ms):

#     # times = time.time()
#     endpoint = sanitize_endpoint(endpoint=endpoint)
#     registry = CollectorRegistry()

#     try:

#         # Set the Gauge value for the specific endpoint, status_code, and method
#         http_api_request_latency.labels(
#             endpoint=endpoint,
#             status_code=str(status_code),  # Ensure status_code is a string
#             method=method,
#             # timestamp=times
#         ).observe(duration_ms)

#         registry.register(http_api_request_latency)

#         # Push to the PushGateway
#         push_to_gateway(
#             'localhost:9091',  # PushGateway address
#             job='util_send_crypto_tax_fail_reports_loader',
#             grouping_key={'endpoint': endpoint},
#             registry=registry
#         )

#         logging.info(f"Successfully recorded and pushed latency for {method} {endpoint} {status_code} ({duration_ms}ms)")

#     except Exception as e:
#         logging.error(f"Failed to record latency for {method} {endpoint} {status_code}. Error: {e}")

# # Example usage for recording latency
# record_latency('/v1/token', 200, 'POST', 11)
# record_latency('/v1/token', 200, 'POST', 12)
# record_latency('/v1/token', 200, 'POST', 13)
# record_latency('/v1/transactions/PINTU-9411d569-9c8b-5a3c-afca-41c4af77edcc', 200, 'POST', 10)
# record_latency('/v1/transactions/PINTU-9411d569-9c8b-5a3c-afca-41c4af77edcc', 200, 'POST', 5)
# record_latency('/v1/transactions/fiat/transactions', 200, 'POST', 13)
# record_latency('/v1/user/9411d569-9c8b-5a3c-afca-41c4af77ed12/profile', 200, 'POST', 14)


# dag_id = 'dag_id'
# task_id = 'task_id'
# status = 'status'
# team = 'team'
# run_id = 'run_id'
# registry = CollectorRegistry()

# _dag_duration_metrics = Gauge(
#     name='airflow_dagrun_duration_ms',
#     documentation='Run Duration of a DAG',
#     labelnames=['team', 'task_id', 'status', 'dag_id', 'run_id'])
# # _dag_duration_metrics.labels(
# #     team=team,
# #     task_id=task_id,
# #     status=status,
# #     dag_id=dag_id,
# #     run_id=run_id
# # ).set(2.6112308)
# # registry.register(_dag_duration_metrics)
# # try:
# #     push_to_gateway(
# #         'localhost:9091',
# #         'qwe',
# #         grouping_key={},
# #         registry=registry
# #     )
# # except Exception as e:
# #     logging.error(
# #         f"Failed to push metrics for DAG {dag_id}, "
# #         f"Task {task_id}: {e}"
# #     )

# dag_id = 'dag_id'
# task_id = 'task_id'
# status = 'status'
# team = 'team'
# run_id = 'run_id1'

# _dag_duration_metrics.labels(
#     team=team,
#     task_id=task_id,
#     status=status,
#     dag_id=dag_id,
#     run_id=run_id
# ).set(1.6112308)
# try:
#     push_to_gateway(
#         'localhost:9091',
#         'qwe',
#         grouping_key={},
#         registry=registry
#     )
# except Exception as e:
#     logging.error(
#         f"Failed to push metrics for DAG {dag_id}, "
#         f"Task {task_id}: {e}"
#     )


# start_time = time.time()
# time.sleep(3.5)
# duration = (time.time() - start_time) * 1000

# print(duration)