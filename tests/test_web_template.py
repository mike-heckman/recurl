import unittest
from unittest.mock import MagicMock
from requests.models import Response
from requests.cookies import RequestsCookieJar
from requests.sessions import Session, CaseInsensitiveDict
from typing import Optional
from recurl.web_template import WebTemplate
from src.recurl import Url


def make_mock(status_code: Optional[int] = 200, text: Optional[str] = "OK") -> MagicMock:
    """
    Create a request mock object
    """
    response = MagicMock(spec=Response)
    response.status_code = status_code
    response.text = text

    session = MagicMock(spec=Session)
    session.headers = CaseInsensitiveDict()
    session.cookies = RequestsCookieJar()
    session.request.return_value = response
    session.response = response

    return session

SUCCESS = 200
SUCCESS_TEXT = "OK"

class TestWebTemplate(unittest.TestCase):

    def test_initialize_webtemplate(self):
        mock_session = make_mock()
        # Test for initialization with a URL and default parameters
        web_template = WebTemplate(
            url="https://www.example.com",
            method="GET",
            data=None,
            headers=["Content-Type: application/json"],
            cookies=["cookie_name=cookie_value"],
            verify=True,
            session = mock_session
        )

        # Test that the WebTemplate object is initialized correctly
        self.assertEqual(web_template.method, "GET")
        self.assertEqual(web_template.url, "https://www.example.com")
        self.assertTrue("content-type" in web_template.headers)
        self.assertEqual(web_template.headers["Content-Type"], "application/json")
        self.assertEqual(len(web_template.cookies), 1)

    def test_send_request(self):
        # Mock the response from `requests.request` method
        mock_session = make_mock(SUCCESS, SUCCESS_TEXT)
        web_template = WebTemplate(url="https://www.example.com", session=mock_session)

        # Send the request and check the response
        response = web_template.send()
        self.assertEqual(response.status_code, SUCCESS)
        self.assertEqual(response.text, SUCCESS_TEXT)
        mock_session.request.assert_called_once()

    def test_send_request_with_custom_params(self):
        # Mock the response from `requests.request` method
        mock_session = make_mock(SUCCESS, SUCCESS_TEXT)

        web_template = WebTemplate(url="https://www.example.com",
                                 method="POST",
                                 data={"key": "value"},
                                 session=mock_session)

        # Send the request and check the response
        response = web_template.send()
        self.assertEqual(response.status_code, SUCCESS)
        self.assertEqual(response.text, SUCCESS_TEXT)
        mock_session.request.assert_called_once()

    def test_add_cookies(self):
        # Initialize WebTemplate object
        web_template = WebTemplate(url="https://www.example.com")

        # Add cookies
        web_template.add_cookies(["cookie1=value1", "cookie2=value2"])

        # Check the cookies set in the Session object
        cookies = web_template.cookies
        self.assertEqual(len(cookies), 2)
        self.assertEqual(cookies.get("cookie1"), "value1")
        self.assertEqual(cookies.get("cookie2"), "value2")

    def test_request_method(self):
        # Mock the response from `requests.request` method
        mock_session = make_mock(SUCCESS, SUCCESS_TEXT)

        web_template = WebTemplate(url="https://www.example.com", session=mock_session)

        # Test using the request method with custom parameters
        response = web_template.request(method="GET", url="https://www.new-url.com", data={"key": "value"})
        self.assertEqual(response.status_code, SUCCESS)
        self.assertEqual(response.text, SUCCESS_TEXT)
        mock_session.request.assert_called_once_with(
            method="POST",
            url="https://www.new-url.com",
            params=None,
            data={"key": "value"},
            headers=None,
            cookies=None,
            files=None,
            auth=None,
            timeout=5.0,
            allow_redirects=True,
            proxies=None,
            hooks=None,
            stream=False,
            verify=None,
            cert=None,
            json=None
        )

    def test_request_method_with_default_values(self):
        # Mock the response from `requests.request` method
        mock_session = make_mock(SUCCESS, SUCCESS_TEXT)

        # Test the request method without any parameters (defaults)
        web_template = WebTemplate(url="https://www.example.com", session=mock_session)
        response = web_template.request()

        self.assertEqual(response.status_code, SUCCESS)
        self.assertEqual(response.text, SUCCESS_TEXT)
        mock_session.request.assert_called_once()

    def test_request_method_with_url_as_url_object(self):
        # Mock the response from `requests.request` method
        mock_session = make_mock(SUCCESS, SUCCESS_TEXT)

        # Test the request method with a Url object
        web_template = WebTemplate(url="https://www.example.com", session=mock_session)
        url_obj = Url(scheme="http", hostname="www.google.com", path="/path")
        response = web_template.request(url=url_obj)

        self.assertEqual(response.status_code, SUCCESS)
        self.assertEqual(response.text, SUCCESS_TEXT)
        mock_session.request.assert_called_once_with(
            method="GET",
            url="http://www.google.com/path",
            params=None,
            data=None,
            headers=None,
            cookies=None,
            files=None,
            auth=None,
            timeout=5.0,
            allow_redirects=True,
            proxies=None,
            hooks=None,
            stream=False,
            verify=None,
            cert=None,
            json=None
        )


if __name__ == "__main__":
    unittest.main()