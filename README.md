# data_uri_parser

Originally from: https://gist.github.com/zacharyvoase/5538178

Data URI manipulation made easy.

This isn't very robust, and will reject a number of valid data URIs. However, it meets the most useful case: a mimetype, a charset, and the base64 flag.

### Parsing

```python
>>> uri = DataURI('data:text/plain;charset=utf-8;base64,VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wZWQgb3ZlciB0aGUgbGF6eSBkb2cu')
>>> uri.mimetype
'text/plain'
>>> uri.charset
'utf-8'
>>> uri.is_base64
True
>>> uri.data
'The quick brown fox jumped over the lazy dog.'
```

Note that `DataURI.data` won't decode the data bytestring into a unicode string based on the charset.


### Creating from a string

```python
>>> made = DataURI.make('text/plain', charset='us-ascii', base64=True, data='This is a message.')
>>> made
DataURI('data:text/plain;charset=us-ascii;base64,VGhpcyBpcyBhIG1lc3NhZ2Uu')
>>> made.data
'This is a message.'
```


### Creating from a file

This is really just a convenience method.

```python
>>> png_uri = DataURI.from_file('somefile.png')
>>> png_uri.mimetype
'image/png'
>>> png_uri.data
'\x89PNG\r\n...'
```
