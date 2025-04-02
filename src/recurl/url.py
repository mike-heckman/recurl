
import logging

from dataclasses import dataclass
from immutabledict import immutabledict
from typing import Any, Optional
from urllib.parse import parse_qs, unquote_plus, urljoin, urlparse, urlunparse, urlencode

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Url:
    """
    Create an immutable Url object that still provides dictionary-like access to the query and params parameters.
    """
    scheme: Optional[str] = ""
    hostname: Optional[str] = ""
    port: Optional[int] = None
    path: Optional[str] = ""
    query: Optional[immutabledict[str, Any]] = immutabledict()
    params: Optional[immutabledict[str, Any]] = immutabledict()
    fragment: Optional[str] = ""
    username: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def parse(cls, url: str) -> "Url":
        """
        Parse a string url into a URL object
        :param url: A string url
        :return: A new URL object
        """
        logger.debug("Parsing requested url '%s'", url)
        parsed = urlparse(url)
        fragment = "" if parsed.fragment is None else unquote_plus(parsed.fragment)

        return Url(scheme=parsed.scheme,
                   hostname = parsed.hostname,
                   port = parsed.port,
                   path = unquote_plus(parsed.path),
                   query = immutabledict(parse_qs(parsed.query, keep_blank_values=True)),
                   params = immutabledict(parse_qs(parsed.params, keep_blank_values=True, separator=";")),
                   fragment = fragment
                   )

    def __repr__(self) -> str:
        """
        Represent our self as a string of the url content
        :return: string url
        """
        return self.url

    def __str__(self) -> str:
        """
        Return just the string url when called

        :return: string url
        """
        return self.url

    def __add__(self, other: str) -> "Url":
        """
        Combines the current object with another Url object, a string or None

        :param other: Another Url object
        :return: A new combined Url object
        """
        return Url.parse(urljoin(self.url, str(other)))

    @property
    def url(self) -> str:
        """
        Return the url

        :return: The url represented by all the components in the object
        """
        local_netloc = self.hostname if self.port is None else f"{self.hostname}:{str(self.port)}"

        output = str(urlunparse([
            self.scheme,
            local_netloc,
            self.path,
            urlencode({} if self.params is None else self.params),
            urlencode({} if self.query is None else self.query),
            self.fragment
        ]))

        logger.debug("Returning requested url string '%s'", output)
        return output

    def update(self,
               scheme: Optional[str] = None,
               hostname: Optional[str] = None,
               port: Optional[int] = None,
               path: Optional[str] = None,
               query: Optional[dict] = None,
               params: Optional[dict] = None,
               fragment: Optional[str] = None,
               username: Optional[str] = None,
               password: Optional[str] = None
               ) -> "Url":
        """
        Creates a new Url object, using defaults from the current object with overrides for any specified
        parameters.

        :param scheme: The scheme (protocol) provided
        :param hostname: The server hostname
        :param port: The port to use
        :param path: The path
        :param query: Query parameters as a dictionary of key/value pairs
        :param params: URL parameters as a dictionary of key/value pairs
        :param fragment: The fragment portion of the URL
        :param username: A username to use
        :param password: A password to use
        :return: Url Object
        """
        return Url(scheme = self.scheme if scheme is None else scheme,
                   hostname = self.hostname if hostname is None else hostname,
                   port = self.port if port is None else port,
                   path = unquote_plus(self.path) if path is None else path,
                   query = self.query if query is None else self.query.update(query),
                   params = self.params if params is None else self.params.update(params),
                   fragment = unquote_plus(self.fragment) if fragment is None else fragment,
                   username = self.username if username is None else username,
                   password = self.password if password is None else password)
