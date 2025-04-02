# -*- coding: utf-8 -*-
import argparse
import shlex

from argparse import Namespace

from requests import Session
from typing import Any, Optional

from .web_template import WebTemplate

def init_parser() -> argparse.ArgumentParser:
    """
    Initialize a fresh ArgumentParser object

    :return: argparse.ArgumentParser instance
    """
    parser = argparse.ArgumentParser(description="Parse a curl bash command")

    parser.add_argument('command', help="The curl command")

    # URL (positional argument)
    parser.add_argument('url', help="The URL for the request")

    # HTTP method (GET, POST, PUT, DELETE, etc.)
    parser.add_argument('-X', '--request', help="Specify the request method", choices=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'], default='GET')

    # Headers
    parser.add_argument('-H', '--header', action='append', help="Add a header (can be used multiple times)")

    # Data
    parser.add_argument('-d', '--data', help="Send data with the request")
    parser.add_argument('--data-binary', help="Send binary data with the request")
    parser.add_argument('--data-raw', help="Send raw data with the request")

    # Basic authentication
    parser.add_argument('-u', '--user', help="Specify user name and password (user:password)")

    # SSL/TLS options
    parser.add_argument('-k', '--insecure', action='store_true', help="Allow connections to SSL sites without certificates")

    # Proxy
    parser.add_argument('--proxy', help="Use the specified proxy server")
    parser.add_argument('--proxy-user', help="Specify user and password for proxy server")

    # HTTP cookies and session options
    parser.add_argument('-b', '--cookie', help="Send cookies with the request")
    parser.add_argument('--cookie-jar', help="Write cookies to a file")

    return parser

def normalize_newlines(multiline_text: str) -> str:
    """
    Strip newlines and extraneous spaces from input
    :param multiline_text: Multiline string
    :return: stripped string
    """
    return multiline_text.replace(" \\\n", " ")

def handle_proxies_auth(proxy: Optional[str] = None, user: Optional[str] = None) -> (dict|None, tuple[str]|None):
    """
    Parses the proxy and user parameters to return the proxies and auth values
    :param proxy: Proxy declaration
    :param user: Username/password declaration
    :return: The proxy dictionary if defined, the auth tuple if defined
    """
    auth = None
    proxies = None
    if proxy:
        proxy_url = f"http://{proxy}/"
        if user:
            proxy_url = f"http://{user}@{proxy}/"
        proxies = { "http": proxy_url, "https": proxy_url }
    # Support Basic Auth if user and password are provided
    elif user:
        auth = user.split(":")

    return proxies, auth

def post_data(parsed: Namespace) -> Any:
    """
    Return a data element if provided

    :param parsed: List of parsed arguments
    :return: Data Object
    """
    if parsed.data:
        return parsed.data
    elif parsed.data_binary:
        return parsed.data_binary
    elif parsed.data_raw:
        return parsed.data_raw
    return None

def parse_context(curl_command: str, session: Optional[Session] = None) -> WebTemplate:
    """
    Parse the curl command and return a WebTemplate object

    :param curl_command: A single-line or multi-line string containing the curl command
    :param session: An optional requests Session object to construct the request within
    :return: A WebTemplate object
    """
    parsed_args = init_parser().parse_args(shlex.split(normalize_newlines(curl_command)))
    if parsed_args.command != "curl":
        raise ValueError(f"Invalid command '{parsed_args.command}' requested!")

    # add proxy and its authentication if it's available.
    proxies, auth = handle_proxies_auth(parsed_args.proxy, parsed_args.user)

    verify = parsed_args.insecure is not True
    headers = [parsed_args.header] if isinstance(parsed_args.header, str) else parsed_args.header
    cookies = [parsed_args.cookie] if isinstance(parsed_args.cookie, str) else parsed_args.cookie

    req = WebTemplate(url=parsed_args.url,
                      method=parsed_args.request,
                      data=post_data(parsed_args),
                      headers=headers,
                      cookies=cookies,
                      cookiejar_filename=parsed_args.cookie_jar,
                      verify=verify,
                      auth=auth,
                      proxies=proxies,
                      session=session
                      )

    return req
