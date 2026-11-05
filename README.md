# data_uri_parser

<a href="https://pypi.org/project/data_uri_parser/"><img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/data_uri_parser.svg"></a>
<a href="https://pypi.org/project/data_uri_parser/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/data_uri_parser.svg"></a>
<a href="https://opensource.org/licenses/MIT"><img alt="Licence" src="https://img.shields.io/github/license/unmadeworks/data_uri_parser.svg"></a>

_Data URI manipulation made easy._

This isn't very robust, and will reject a number of valid data URIs. However, it meets the most useful case: a mimetype, a charset, and the base64 flag.

## How to install

Requires Python 3.10 or newer.

```sh
pip install data_uri_parser
```

### Parsing

```python
>>> from data_uri_parser import DataURI
>>> uri = DataURI('data:text/plain;charset=utf-8;base64,VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wZWQgb3ZlciB0aGUgbGF6eSBkb2cu')
>>> uri.mimetype
'text/plain'
>>> uri.charset
'utf-8'
>>> uri.is_base64
True
>>> uri.data
b'The quick brown fox jumped over the lazy dog.'
```

For base64 data URIs, `DataURI.data` returns `bytes`; it won't decode them into a string based on the charset. For other data URIs it returns the percent-decoded `str`.


### Creating from bytes

```python
>>> made = DataURI.make('text/plain', charset='us-ascii', base64=True, data=b'This is a message.')
>>> made
'data:text/plain;charset=us-ascii;base64,VGhpcyBpcyBhIG1lc3NhZ2Uu'
>>> made.data
b'This is a message.'
```

With `base64=False`, the data is percent-encoded instead:

```python
>>> DataURI.make('text/plain', base64=False, data=b'Hello, world')
'data:text/plain,Hello%2C%20world'
```


### Creating from a file

This is really just a convenience method.

```python
>>> png_uri = DataURI.from_file('somefile.png')
>>> png_uri.mimetype
'image/png'
>>> png_uri.data
b'\x89PNG\r\n...'
```

## Development

```sh
poetry install
poetry run pytest
poetry run black --check .
poetry run isort --check-only .
```

CI runs the tests on Python 3.10 to 3.14.

## Releasing

Merging to `main` publishes to PyPI, so every PR must bump `version` in `pyproject.toml`. CI fails a PR whose version is already on PyPI.

## Notes

Originally from: https://gist.github.com/zacharyvoase/5538178
