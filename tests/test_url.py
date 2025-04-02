import unittest
from immutabledict import immutabledict
from src.recurl import Url


class TestUrlLibrary(unittest.TestCase):

    def test_url_init(self):
        url = Url(scheme='https', hostname='www.example.com', port=443, path='/path', query=immutabledict({'key': 'value'}))
        self.assertEqual(url.scheme, 'https')
        self.assertEqual(url.hostname, 'www.example.com')
        self.assertEqual(url.port, 443)
        self.assertEqual(url.path, '/path')
        self.assertEqual(url.query, immutabledict({'key': 'value'}))

    def test_url_repr(self):
        url = Url(scheme='https', hostname='www.example.com', port=443, path='/path', query=immutabledict({'key': 'value'}))
        self.assertEqual(repr(url), 'https://www.example.com:443/path?key=value')

    def test_url_str(self):
        url = Url(scheme='https', hostname='www.example.com', port=443, path='/path', query=immutabledict({'key': 'value'}))
        self.assertEqual(str(url), 'https://www.example.com:443/path?key=value')

    def test_url_with_no_query(self):
        url = Url(scheme='https', hostname='www.example.com', path='/path')
        self.assertEqual(str(url), 'https://www.example.com/path')

    def test_new_url(self):
        original_url = Url(scheme='https', hostname='www.example.com', path='/old-path')
        new_url = original_url.update(path='/new-path', query=dict({'newkey': 'newvalue'}))

        self.assertNotEqual(str(original_url), str(new_url))
        self.assertEqual(new_url.path, '/new-path')
        self.assertEqual(new_url.query, immutabledict({'newkey': 'newvalue'}))

    def test_parse_url_with_object(self):
        new_url = Url().parse('https://www.example.com/newpath?q=test')

        self.assertEqual(new_url.scheme, 'https')
        self.assertEqual(new_url.hostname, 'www.example.com')
        self.assertEqual(new_url.port, None)
        self.assertEqual(new_url.path, '/newpath')
        self.assertEqual(new_url.query, immutabledict({'q': ['test']}))


if __name__ == '__main__':
    unittest.main()