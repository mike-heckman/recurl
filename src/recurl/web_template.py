import logging

from http.cookiejar import MozillaCookieJar
from requests import Response
from requests.auth import HTTPBasicAuth, AuthBase
from requests.cookies import RequestsCookieJar
from requests.sessions import Session
from pathlib import Path
from typing import Any, Optional, MutableMapping
from urllib.parse import unquote_plus

from .url import Url

NOT_PROVIDED = "__NOT_PROVIDED__"

logger = logging.getLogger(__name__)

class WebTemplate:
    """
    Represent a potential web request
    """
    def __init__(self,
                 url: str = None,
                 method: str = "GET",
                 data: Optional[dict|bytes] = None,
                 headers: Optional[list[str]] = None,
                 cookies: Optional[list[str]] = None,
                 cookiejar_filename: Optional[str] = None,
                 verify: bool = True,
                 auth: Optional[AuthBase|str] = None,
                 proxies: Optional[dict] = None,
                 session: Optional[Session] = None
                 ) -> None:
        """
        :param url: The request URL
        :param method: The request method
        :param data: Data to send for POST requests, if provided will override the method to "POST"
        :param headers: Headers to include
        :param cookies: Cookies to include
        :param verify: (optional) Either a boolean, in which case it controls whether we verify the server's TLS
            certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to ``True``.
            When set to ``False``, requests will accept any TLS certificate presented by the server, and will ignore
            hostname mismatches and/or expired certificates, which will make your application vulnerable to
            man-in-the-middle (MitM) attacks. Setting verify to ``False`` may be useful during local development or
            testing.
        :param auth: (optional) Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
        :param proxies: (optional) Dictionary mapping protocol or protocol and hostname to the URL of the proxy.
        :param session: (optional) A requests.sessions.Session object to use for cookie and header retention,
            created automatically if not provided
        """
        self.session = Session() if session is None else session

        if data is not None:
            self.method = "POST"
            self.data = data
        else:
            self.method = "GET" if method is None or len(method) == 0 else method.upper()

        self.request_url = Url.parse(url)
        self.params = self.request_url.params
        self.data = data
        self.verify = verify
        self.proxies = proxies

        if cookiejar_filename is not None:
            self.cookiejar_filename = cookiejar_filename
            if Path(self.cookiejar_filename).exists():
                jar = MozillaCookieJar(self.cookiejar_filename)
                jar.load(ignore_discard=True, ignore_expires=True)
                # Session cookie attribute can take any type of HTTPCookieJar instance
                # https://github.com/psf/requests/blob/main/src/requests/cookies.py#L185
                self.session.cookies = jar

        if cookies:
            self.add_cookies(cookies)

        if auth is None and self.request_url.username is not None:
            self.auth = HTTPBasicAuth(self.request_url.username, self.request_url.password)
        elif isinstance(auth, str):
            try:
                self.auth = HTTPBasicAuth(*auth.split(':'))
            except Exception:
                logger.error(f"Caught exception trying to promote the string {auth} to HTTPBasicAuth!")
                raise
        else:
            self.auth = auth

        if headers:
            self._parse_headers(headers)

    def _parse_headers(self, headers: list[str]) -> None:
        """
        Parse the headers
        :param headers:
        :return:
        """
        for header in headers:
            header_name, header_value = header.split(":", 1)
            header_value = header_value.strip()
            if header_name.lower().strip("$") == "cookie":
                self.add_cookies([header_value])
            else:
                self.session.headers[header_name] = header_value

    @property
    def url(self) -> str:
        """
        Provide a string representation of the url object

        :return: A string
        """
        return self.request_url.url

    @property
    def cookies(self) -> RequestsCookieJar:
        """
        Returns the active CookieJar from the Session object
        :return: The cookiejar
        """
        return self.session.cookies

    @property
    def headers(self) -> MutableMapping[str, str | bytes]:
        """
        Returns the active header set from the Session object
        :return: The headers
        """
        return self.session.headers

    def add_cookies(self,
                    cookie_set: list[str],
                    domain: Optional[str] = NOT_PROVIDED,
                    path: Optional[str] = NOT_PROVIDED) -> None:
        """
        Parse the cookie string into a list of cookie dictionaries

        :param cookie_set: String containing one or more cookie key/value sets key=value;key2=value2, etc.
        :param domain: Domain name to use
        :param path: Path to use
        :return: Nothing
        """
        for cookie_str in cookie_set:
            for cookie in cookie_str.split(";"):
                cookie_name, cookie_value = cookie.strip().split("=", 1)
                self.session.cookies.set(name=unquote_plus(cookie_name).strip(),
                                         value=unquote_plus(cookie_value).strip(),
                                         domain=self.request_url.hostname if domain is NOT_PROVIDED else domain,
                                         path="/" if path is NOT_PROVIDED else path
                                         )

        return None

    def save_cookies(self,
                     filename: Optional[str] = None,
                     ignore_discard: Optional[bool] = True,
                     ignore_expires: Optional[bool] = True) -> str:
        """
        Save cookies to either the filename specified or the cookie_filename provided during
        instantiation.

        :param filename: File path where to write the cookies
        :param ignore_discard: Save cookies even if they'd normally be discarded
        :param ignore_expires: Save cookies even if they are expired
        :return: filename
        """
        filename = self.cookiejar_filename if filename is None else filename

        # If this isn't a MozillaCookieJar, make it into one
        if not isinstance(self.session.cookies, MozillaCookieJar):
            jar = MozillaCookieJar()
            for cookie in self.session.cookies:
                jar.set_cookie(cookie)

            # Session cookie attribute can take any type of HTTPCookieJar instance
            # https://github.com/psf/requests/blob/main/src/requests/cookies.py#L185
            self.session.cookies = jar

        self.session.cookies.save(filename, ignore_discard=ignore_discard, ignore_expires=ignore_expires)
        return filename

    def send(self,
             timeout: Optional[float] = None,
             allow_redirects: Optional[bool] = None,
             hooks: Optional[dict] = None,
             stream: Optional[bool] = None,
             cert: Optional[str|tuple] = None
             ) -> Response:
        """
        Send the initialized request and return a response object

        :param timeout: (optional) How long to wait for the server to send data before giving up, as a float, or a
            :ref:`(connect timeout, read timeout) <timeouts>` tuple.
        :param allow_redirects: (optional) Set to True by default.
        :param hooks: (optional) Dictionary mapping hook name to one event or list of events, event must be callable.
        :param stream: (optional) whether to immediately download the response content. Defaults to ``False``.
        :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        :return: requests.Response
        """
        return self.session.request(method=self.method,
                                    url=self.url,
                                    params=self.params,
                                    data=self.data,
                                    auth=self.auth,
                                    proxies=self.proxies,
                                    verify=self.verify,
                                    timeout=timeout,
                                    allow_redirects=allow_redirects,
                                    hooks=hooks,
                                    stream=stream,
                                    cert=cert
                                    )

    def request(
            self,
            method: Optional[str] = NOT_PROVIDED,
            url: Optional[Url|str] = NOT_PROVIDED,
            params: Optional[dict|str] = NOT_PROVIDED,
            data: Optional[dict|str|bytes] = NOT_PROVIDED,
            headers: Optional[dict|str] = None,
            cookies: Optional[dict|str] = None,
            files: Optional[dict] = None,
            auth: Optional[tuple] = None,
            timeout: Optional[float] = 5.0,
            allow_redirects: bool = True,
            proxies: Optional[dict] = None,
            hooks: Optional[dict] = None,
            stream: bool = False,
            verify: Optional[bool] = None,
            cert: Optional[str|tuple] = None,
            json: Optional[Any] = None,
    ) -> Response:
        """
        If called without any parameters will launch the decoded request in WebTemplate.  Optionally,
        parameters can be provided to override one or more values in the originating request.

        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
        :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
        :param files: (optional) Dictionary of ``'filename': file-like-objects`` for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) How long to wait for the server to send data before giving up,
            as a float, or a :ref:`(connect timeout, read timeout) <timeouts>` tuple.
        :param allow_redirects: (optional) Set to True by default.
        :param proxies: (optional) Dictionary mapping protocol or protocol and hostname to the URL of the proxy.
        :param hooks: (optional) Dictionary mapping hook name to one event or list of events, event must be callable.
        :param stream: (optional) whether to immediately download the response content. Defaults to ``False``.
        :param verify: (optional) Either a boolean, in which case it controls whether we verify the server's TLS
            certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to ``True``.
            When set to ``False``, requests will accept any TLS certificate presented by the server, and will ignore
            hostname mismatches and/or expired certificates, which will make your application vulnerable to
            man-in-the-middle (MitM) attacks. Setting verify to ``False`` may be useful during local development or
            testing.
        :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        :rtype: requests.Response
        """
        url = self.url if url is NOT_PROVIDED or url is None else str(url)
        if data is not NOT_PROVIDED and data is not None:
            method = "POST"

        if params is NOT_PROVIDED:
            params = None

        return self.session.request(
            method=self.method if method is NOT_PROVIDED else method.upper(),
            url=url,
            params=params,
            data=self.data if data is NOT_PROVIDED else data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=self.auth if auth is None else auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json
        )
