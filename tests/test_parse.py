import unittest
from unittest.mock import patch, MagicMock
from recurl import parse_context, WebTemplate

class TestParseContext(unittest.TestCase):

    @patch('recurl.parse.WebTemplate')  # Mock WebTemplate class
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_context_valid(self, mock_parse_args, mock_web_template):
        # Simulate the args that argparse would normally receive from the command line
        mock_parse_args.return_value = MagicMock(
            command="curl",
            url="http://example.com",
            request="GET",
            header=["Accept: application/json"],
            data=None,
            data_binary=None,
            data_raw=None,
            user=None,
            insecure=False,
            proxy=None,
            cookie=None,
            cookie_jar=None
        )

        # Call the function to parse the context
        mock_web_template.return_value = MagicMock()
        result = parse_context("curl http://example.com -H 'Accept: application/json'")

        # Assertions to check that WebTemplate is created with the correct arguments
        mock_web_template.assert_called_once_with(
            url="http://example.com",
            method="GET",
            data=None,
            headers=["Accept: application/json"],
            cookies=None,
            cookiejar_filename=None,
            verify=True,  # Since insecure is False
            auth=None,
            proxies=None,
            session=None
        )

    @patch('recurl.parse.WebTemplate')
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_context_with_basic_auth(self, mock_parse_args, mock_web_template):
        # Simulate the args for a command with basic authentication
        mock_parse_args.return_value = MagicMock(
            command="curl",
            url="http://example.com",
            request="GET",
            header=["Accept: application/json"],
            data=None,
            data_binary=None,
            data_raw=None,
            user="username:password",  # Simulating basic auth
            insecure=False,
            proxy=None,
            cookie=None,
            cookie_jar=None
        )

        # Call the function to parse the context
        mock_web_template.return_value = MagicMock()
        result = parse_context("curl http://example.com -H 'Accept: application/json' -u 'username:password'")

        # Assertions to check that WebTemplate is created with the correct authentication
        mock_web_template.assert_called_once_with(
            url="http://example.com",
            method="GET",
            data=None,
            headers=["Accept: application/json"],
            cookies=None,
            cookiejar_filename=None,
            verify=True,  # Since insecure is False
            auth=["username", "password"],
            proxies=None,
            session=None
        )

    @patch('recurl.parse.WebTemplate')
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_context_with_proxy(self, mock_parse_args, mock_web_template):
        # Simulate the args for a command with proxy settings
        mock_parse_args.return_value = MagicMock(
            command="curl",
            url="http://example.com",
            request="GET",
            header=["Accept: application/json"],
            data=None,
            data_binary=None,
            data_raw=None,
            user="username:password",  # Simulating proxy authentication
            insecure=False,
            proxy="proxy.example.com:8080",
            cookie=None,
            cookie_jar=None
        )

        # Call the function to parse the context
        mock_web_template.return_value = MagicMock()
        result = parse_context("curl http://example.com -H 'Accept: application/json' --proxy 'proxy.example.com:8080' -u 'username:password'")

        # Assertions to check that WebTemplate is created with the correct proxy settings
        mock_web_template.assert_called_once_with(
            url="http://example.com",
            method="GET",
            data=None,
            headers=["Accept: application/json"],
            cookies=None,
            cookiejar_filename=None,
            verify=True,  # Since insecure is False
            auth=None,
            proxies={
                "http": "http://username:password@proxy.example.com:8080/",
                "https": "http://username:password@proxy.example.com:8080/"
            },
            session=None
        )

    @patch('recurl.parse.WebTemplate')
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_context_with_insecure_ssl(self, mock_parse_args, mock_web_template):
        # Simulate the args for a command with the insecure flag set to True
        mock_parse_args.return_value = MagicMock(
            command="curl",
            url="http://example.com",
            request="GET",
            header=["Accept: application/json"],
            data=None,
            data_binary=None,
            data_raw=None,
            user=None,
            insecure=True,  # This should disable SSL verification
            proxy=None,
            cookie=None,
            cookie_jar=None
        )

        # Call the function to parse the context
        mock_web_template.return_value = MagicMock()
        result = parse_context("curl http://example.com -H 'Accept: application/json' -k")

        # Assertions to check that WebTemplate is created with SSL verification disabled
        mock_web_template.assert_called_once_with(
            url="http://example.com",
            method="GET",
            data=None,
            headers=["Accept: application/json"],
            cookies=None,
            cookiejar_filename=None,
            verify=False,  # SSL verification should be disabled
            auth=None,
            proxies=None,
            session=None
        )

if __name__ == '__main__':
    unittest.main()