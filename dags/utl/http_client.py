# Copyright (c) PT Pintu Kemana Saja 2024 All Rights Reserved.

import time
import ssl
import requests
from prometheus_client import (CollectorRegistry, Counter, Summary,
                               push_to_gateway)
import logging
from requests.adapters import HTTPAdapter
# import json
# from airflow.models import Variable

pushgateway_config = {
    'host': 'localhost',
    'port': 9091
}
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_pushgateway_url():
    return f"{pushgateway_config.get('host')}:{pushgateway_config.get('port')}"


class TLSAdapter(HTTPAdapter):
    """A Transport Adapter that uses an explicit TLS version."""
    def __init__(self, tls_version=None, *args, **kwargs):
        if tls_version is None:
            tls_version = "TLSv1.2"
        self.tls_version = tls_version
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.options &= ~ssl.OP_NO_TLSv1_3 & ~ssl.OP_NO_TLSv1

        if tls_version == "TLSv1.1":
            self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_1
            self.ssl_context.maximum_version = ssl.TLSVersion.TLSv1_1
        elif tls_version == "TLSv1.2":
            self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            self.ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


class HttpClient:
    """
        HTTP client with integrated Prometheus metrics and Pushgateway support.
    """
    def __init__(
        self,
        context,
        base_url,
        auth=None,
        pushgateway_url=get_pushgateway_url(),
        timeout=None,
        adapter=None,
    ):
        self.auth = auth
        self.base_url = base_url
        self.context = context
        self.pushgateway_url = pushgateway_url
        self.registry = CollectorRegistry()
        self.timeout = timeout
        self.session = requests.Session()
        if adapter is not None:
            for prefix in adapter:
                self.session.mount(prefix, adapter[prefix])
        self._init_metrics()

    def _init_metrics(self):
        self._request_latency = Summary(
            name='api_latency',
            documentation='Request latency (ms) from each HTTP call to an API',
            labelnames=['endpoint', 'status_code'],
            registry=self.registry
        )

    def request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        start_time = time.time()
        try:
            response = self.session.request(method, url, auth=self.auth,
                                            timeout=self.timeout, **kwargs)
            duration = (time.time() - start_time) * 1000
        except Exception as e:
            logging.error(f"Failed to perform {method} request to {url}: {e}")
            raise

        self._request_latency.labels(
            endpoint=endpoint,
            status_code=response.status_code
        ).observe(duration)

        # try:
        #     push_to_gateway(
        #         self.pushgateway_url,
        #         self.context,
        #         grouping_key={'endpoint': endpoint},
        #         registry=self.registry
        #     )
        # except Exception as e:
        #     logging.error(
        #         f"Failed to push metrics for endpoint {endpoint}"
        #         f"Context {self.context}: {e}"
        #     )
        return response

    def get(self, endpoint, params=None, headers=None, **kwargs):
        r"""Sends a GET request.

        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("GET", endpoint, params=params,
                            headers=headers, **kwargs)

    def options(self, endpoint, headers=None, **kwargs):
        r"""Sends an OPTIONS request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("OPTIONS", endpoint, headers=headers, **kwargs)

    def head(self, endpoint, headers=None, **kwargs):
        r"""Sends a HEAD request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes. If
            `allow_redirects` is not provided, it will be set to `False` (as
            opposed to the default :meth:`request` behavior).
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", False)
        return self.request("HEAD", endpoint, headers=headers, **kwargs)

    def post(self, endpoint, data=None, json=None, headers=None, **kwargs):
        r"""Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in
            the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("POST", endpoint, data=data, json=json,
                            headers=headers, **kwargs)

    def put(self, endpoint, data=None, headers=None, **kwargs):
        r"""Sends a PUT request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in
            the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("PUT", endpoint, data=data,
                            headers=headers, **kwargs)

    def patch(self, endpoint, data=None, headers=None, **kwargs):
        r"""Sends a PATCH request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in
            the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("PATCH", endpoint, data=data,
                            headers=headers, **kwargs)

    def delete(self, endpoint, headers=None, **kwargs):
        r"""Sends a DELETE request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("DELETE", endpoint, headers=headers, **kwargs)