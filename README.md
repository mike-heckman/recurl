# recurl Python Library

`recurl` is a Python library designed to convert `curl` command-line statements into equivalent Python `requests` code. It helps users transition from using `curl` for HTTP requests to Python code with ease.

## Features
- Converts `curl` commands to Python `requests` code.
- Simplifies the process of using `curl` for quick testing and then switching to Python for more complex logic.

## Installation
You can install `recurl` via pip:
```bash
pip install recurl
```

## Example Use Case:
Given a curl command like:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' http://example.com/api
```
Recurl can convert it to a Python requests code equivalent.

For more detailed usage, see the demo.py file in included in the repository.
