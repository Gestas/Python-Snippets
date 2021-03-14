"""My generally generic requests wrapper."""
# https://github.com/Gestas/Python-Snippets/
# See https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/

import logging
from urllib.parse import urljoin

import requests
from requests import Request, Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class DoHTTP:
    """Do a HTTP request."""

    def __init__(self, method, endpoint):
        self._method = method
        self._endpoint = endpoint

        self._retries = Retry(
            total=20,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=[
                "HEAD",
                "GET",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
                "PROPFIND",
            ],
            backoff_factor=10,
        )

    def request(self, path, endpoint=None, method=None, **kwargs):
        """Make a http request.
        :param path: Path for the request
        :type path: str
        :param endpoint: Request endpoint
        :type endpoint: str
        :param method: Request method
        :type method: str
        :return: The response
        :rtype: requests.response
        """
        _path = path
        _endpoint = endpoint or self._endpoint
        _method = method or self._method
        _data = kwargs.get("data")
        _proxy = kwargs.get("proxy")
        _params = kwargs.get("params")
        _basic_auth = kwargs.get("auth")
        _verify = kwargs.get("verify", True)
        _raise = kwargs.get("do_raise", True)
        _server_timeout = kwargs.get("timeout", 30)
        _allow_redirects = kwargs.get("allow_redirects", True)
        _url = urljoin(_endpoint, _path)

        _headers = {}
        if "headers" in kwargs:
            _headers.update(kwargs.get("headers"))
        if "user_agent" in kwargs:
            _headers["User-Agent"] = kwargs.get("user_agent")

        _requests_session = Session()
        _requests_session.mount(
            "http://", TimeoutHTTPAdapter(max_retries=self._retries)
        )
        _requests_session.mount(
            "https://", TimeoutHTTPAdapter(max_retries=self._retries)
        )
        logging.debug(f"HTTP REQUEST URL: {_url}")
        logging.debug(f"HTTP REQUEST METHOD: {_method}")
        logging.debug(f"HTTP REQUEST DATA: {_data}")
        logging.debug(f"HTTP REQUEST PARAMS: {_params}")
        logging.debug(f"HTTP REQUEST BASIC AUTH: {_basic_auth}")
        logging.debug(f"HTTP REQUEST HEADERS: {_headers}")
        logging.debug(f"HTTP REQUEST PROXY: {_proxy}")
        logging.debug(f"VERIFYING SERVER CERTIFICATE: {str(_verify)}")

        _request = Request(
            method=_method,
            url=_url,
            auth=_basic_auth,
            data=_data,
            params=_params,
            headers=_headers,
        )
        _prepared_request = _request.prepare()
        try:
            _response = _requests_session.send(
                _prepared_request,
                timeout=_server_timeout,
                proxies=_proxy,
                verify=_verify,
                allow_redirects=_allow_redirects,
            )
            logging.debug(f"HTTP RESPONSE CODE: {_response.status_code}")
            logging.debug(f"HTTP RESPONSE HEADERS: {_response.headers}")
            logging.debug(f"HTTP RESPONSE CONTENT: {_response.content}")
            if _raise:
                _response.raise_for_status()
            return _response
        except requests.exceptions.HTTPError as err:
            logger.error(f"Error: {err}")
            raise err
        except requests.exceptions.SSLError as err:
            logger.warning(f"HTTP TLS ERROR: {str(err)}")
            raise err
        except requests.exceptions.Timeout as err:
            logger.warning(f"HTTP Timeout ERROR: {str(err)}")
            raise err
        except requests.exceptions.ConnectionError as err:
            logger.warning(f"HTTP Connection ERROR: {str(err)}")
            raise err
        except Exception as err:
            logger.warning(f"HTTP WARNING: {str(err)}")
            raise err


class TimeoutHTTPAdapter(HTTPAdapter):
    """Adapter to manage retries after timeouts and 429, 50? responses."""

    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        """Modifies the request to include our retry strategy.
        :param request: The prepared request
        :type request: PreparedRequest
        :param kwargs: Should include the requests timeout as "timeout".
        :type kwargs: dict
        :return: The updated request
        :rtype: PreparedRequest
        """
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
