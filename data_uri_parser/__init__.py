__version__ = "0.1.0"

import mimetypes
import re
import textwrap
import urllib
from base64 import b64decode, encodebytes

MIMETYPE_REGEX = r"[\w]+\/[\w\-\+\.]+"
_MIMETYPE_RE = re.compile("^{}$".format(MIMETYPE_REGEX))

CHARSET_REGEX = r"[\w\-\+\.]+"
_CHARSET_RE = re.compile("^{}$".format(CHARSET_REGEX))

DATA_URI_REGEX = (
    r"data:"
    + r"(?P<mimetype>{})?".format(MIMETYPE_REGEX)
    + r"(?:\;charset\=(?P<charset>{}))?".format(CHARSET_REGEX)
    + r"(?P<base64>\;base64)?"
    + r",(?P<data>.*)"
)
_DATA_URI_RE = re.compile(r"^{}$".format(DATA_URI_REGEX), re.DOTALL)

CONTEXT_TYPE_REGEX = r"(?P<mimetype>{})?".format(
    MIMETYPE_REGEX
) + r"(?:\;charset\=(?P<charset>{}))?".format(CHARSET_REGEX)

_CONTEXT_URI_RE = re.compile(r"^{}$".format(CONTEXT_TYPE_REGEX), re.DOTALL)


class DataURIValueError(ValueError):
    pass


class DataURI(str):
    @classmethod
    def make(cls, mimetype, data, charset=None, base64=True):
        parts = ["data:"]
        if mimetype is not None:
            if not _MIMETYPE_RE.match(mimetype):
                raise DataURIValueError("Invalid mimetype: %r" % mimetype)
            parts.append(mimetype)
        if charset is not None:
            if not _CHARSET_RE.match(charset):
                raise DataURIValueError("Invalid charset: %r" % charset)
            parts.extend([";charset=", charset])
        if base64:
            parts.append(";base64")
            encoded_data = encodebytes(data).decode("ascii").replace("\n", "")
        else:
            encoded_data = urllib.quote(data)
        parts.extend([",", encoded_data])
        return cls("".join(parts))

    @classmethod
    def from_file(cls, filename):
        with open(filename, "rb") as fp:
            return cls.from_stream(fp, filename)

    @classmethod
    def from_stream(cls, stream, filename=None):
        stream.seek(0)
        mimetype, _ = mimetypes.guess_type(filename or stream.name, strict=False)
        return cls.make(mimetype, stream.read())

    @classmethod
    def from_response(cls, response):
        content_type = response.headers["Content-Type"]
        match = _CONTEXT_URI_RE.match(content_type)
        if not match:
            raise DataURIValueError(
                f"Not a valid response content type: {content_type}"
            )

        mimetype = match.group("mimetype") or None
        charset = match.group("charset") or None
        return cls.make(mimetype, response.content, charset=charset)

    def to_content_bytes_and_extension(self):
        extension = mimetypes.guess_extension(self.mimetype)
        return self.data, extension

    def __new__(cls, *args, **kwargs):
        uri = super().__new__(cls, *args, **kwargs)
        uri._parse  # Trigger any ValueErrors on instantiation.
        return uri

    def wrap(self, width=76):
        return type(self)("\n".join(textwrap.wrap(self, width)))

    @property
    def mimetype(self):
        return self._parse[0]

    @property
    def charset(self):
        return self._parse[1]

    @property
    def is_base64(self):
        return self._parse[2]

    @property
    def data(self):
        return self._parse[3]

    @property
    def _parse(self):
        match = _DATA_URI_RE.match(self)
        if not match:
            raise DataURIValueError("Not a valid data URI: %r" % self)
        mimetype = match.group("mimetype") or None
        charset = match.group("charset") or None
        if match.group("base64"):
            data = b64decode(match.group("data"))
        else:
            data = urllib.unquote(match.group("data"))
        return mimetype, charset, bool(match.group("base64")), data
