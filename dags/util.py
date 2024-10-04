import json
import time

import requests
import statsd
from airflow.models import Variable


class HttpClient:
    def __init__(self, context, base_url):
        self.base_url = base_url
        self.context = context
        # config = json.loads(Variable.get("statsd_config"))
        client = statsd.StatsClient(host='statsd-exporter',port='8125',prefix='airflow')

        self.statsd_client = client

    def _send_metrics(self, endpoint, status_code, duration):
        self.statsd_client.incr(f"api.{self.context}.{endpoint}.status_code.{status_code}")
        self.statsd_client.timing(f"api.{self.context}.{endpoint}.duration", duration)

    def request(self, method:str, endpoint:str, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        start_time = time.time()
        response = requests.request(method, url, **kwargs)
        duration = (time.time() - start_time) * 1000
        self._send_metrics(endpoint, response.status_code, duration)
        return response

    def get(self, endpoint, params=None, **kwargs):
        r"""Sends a GET request.

        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("GET", endpoint, params=params, **kwargs)


    def options(self, endpoint, **kwargs):
        r"""Sends an OPTIONS request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("OPTIONS", endpoint, **kwargs)


    def head(self, endpoint, **kwargs):
        r"""Sends a HEAD request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes. If
            `allow_redirects` is not provided, it will be set to `False` (as
            opposed to the default :meth:`request` behavior).
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", False)
        return self.request("HEAD", endpoint, **kwargs)


    def post(self, endpoint, data=None, json=None, **kwargs):
        r"""Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("POST", endpoint, data=data, json=json, **kwargs)


    def put(self, endpoint, data=None, **kwargs):
        r"""Sends a PUT request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("PUT", endpoint, data=data, **kwargs)


    def patch(self, endpoint, data=None, **kwargs):
        r"""Sends a PATCH request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("PATCH", endpoint, data=data, **kwargs)


    def delete(self, endpoint, **kwargs):
        r"""Sends a DELETE request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("DELETE", endpoint, **kwargs)

