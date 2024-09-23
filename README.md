# Env Setup

## Airflow Docker

```bash
mkdir airflow-env
cd airflow-env
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.2/docker-compose.yaml'
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
docker compose up airflow-init
docker compose up -d
```

Uncomment this line on docker-compose file  
`AIRFLOW_CONFIG: '/opt/airflow/config/airflow.cfg'`

Some config is overriden by some lines in docker-compose file, search for &airflow-common-env and you will find it

Update statsd_on to true

## Statsd-Exporter

Configure statsd-exporter to the docker-compose:

```yaml
  statsd-exporter:
    image: prom/statsd-exporter
    container_name: airflow-statsd-exporter
    command: "--statsd.listen-udp=:8125 --web.listen-address=:9102"
    ports:
        - 9123:9102
        - 8125:8125/udp
```

## Logging

Based on this tutorial <https://www.elastic.co/blog/getting-started-with-the-elastic-stack-and-docker-compose>
