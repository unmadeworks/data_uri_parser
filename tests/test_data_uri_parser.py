from base64 import encodebytes
from io import BytesIO
from os.path import dirname, join, realpath

import pytest
from pytest import fixture

from data_uri_parser import DataURI, DataURIValueError


@fixture(scope="function")
def dummy_stream_object():
    class TestStream(BytesIO):
        def __init__(self, name, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.name = name

    return TestStream


@fixture(scope="function")
def asset_path_filename():
    current_folder = dirname(realpath(__file__))
    filename = join(current_folder, "assets/data_uri.svg")

    return filename


@fixture(scope="function")
def dummy_content_and_data_uri():
    content_data = b"some bytes of a PDF"
    enconded_data = encodebytes(content_data).decode("ascii").replace("\n", "")
    return content_data, f"data:application/pdf;base64,{enconded_data}"


@fixture(scope="function")
def dummy_content_and_data_uri_non_b64():
    return (
        "foo bar:1234,5678",
        "data:text/plain;charset=UTF-8,foo%20bar:1234,5678",
    )


@fixture(scope="function")
def dummy_content_and_data_uri_non_b64_with_whitespace():
    return (
        "foo bar:1234,5678",
        "data:text/plain; charset=UTF-8,foo%20bar:1234,5678",
    )


@fixture(scope="function")
def dummy_response_object():
    class TestResponse:
        def __init__(self, content_type, content):
            self.content = content
            self.headers = {"Content-Type": content_type}

    return TestResponse


@fixture(scope="function")
def dummy_content_and_data_uri():
    content_data = b"some bytes of a PDF"
    enconded_data = encodebytes(content_data).decode("ascii").replace("\n", "")
    return content_data, f"data:application/pdf;base64,{enconded_data}"


class TestDataURI:
    def test_not_valid_uri_format(self):
        data_uri = "some plain data not uri format"

        with pytest.raises(DataURIValueError):
            DataURI(data_uri)

    def test_from_bytes_not_valid_uri(self):
        data_uri_bytes = b"data:application/pdf;base64,c29tZSBieXRlcyBvZiBhIFBERg=="

        with pytest.raises(DataURIValueError):
            DataURI(data_uri_bytes)

    def test_from_string_to_data_uri(self, dummy_content_and_data_uri):
        content, dummy_data_uri = dummy_content_and_data_uri
        data_uri = DataURI(dummy_data_uri)

        assert type(data_uri) == DataURI
        assert data_uri.mimetype == "application/pdf"
        assert data_uri.is_base64
        assert type(data_uri.data) == bytes
        assert data_uri.data == content

    def test_from_string_to_data_uri_non_b64(self, dummy_content_and_data_uri_non_b64):
        content, dummy_data_uri = dummy_content_and_data_uri_non_b64
        data_uri = DataURI(dummy_data_uri)

        assert type(data_uri) == DataURI
        assert data_uri.mimetype == "text/plain"
        assert not data_uri.is_base64
        assert type(data_uri.data) == str
        assert data_uri.data == content

    def test_from_string_to_data_uri_non_b64_with_whitespace(
        self, dummy_content_and_data_uri_non_b64_with_whitespace
    ):
        content, dummy_data_uri = dummy_content_and_data_uri_non_b64_with_whitespace
        data_uri = DataURI(dummy_data_uri)

        assert type(data_uri) == DataURI
        assert data_uri.mimetype == "text/plain"
        assert not data_uri.is_base64
        assert type(data_uri.data) == str
        assert data_uri.data == content

    def test_from_mimetype_and_data_to_data_uri(self):
        mimetype = "image/png"
        data = b"some png data"

        data_uri = DataURI.make(mimetype, data)

        assert type(data_uri) == DataURI
        assert data_uri.mimetype == mimetype
        assert data_uri.is_base64
        assert type(data_uri.data) == bytes
        assert data_uri.data == data

    def test_make_data_uri_from_file(self, asset_path_filename):
        data_uri_from_file = DataURI.from_file(asset_path_filename)

        assert type(data_uri_from_file) == DataURI
        assert data_uri_from_file.mimetype == "image/svg+xml"
        assert data_uri_from_file.is_base64
        assert type(data_uri_from_file.data) == bytes

    def test_make_data_uri_from_stream(self, dummy_stream_object):
        content_file = b"content of a file"
        stream = dummy_stream_object("test.txt", content_file)

        data_uri_from_file = DataURI.from_stream(stream)

        assert type(data_uri_from_file) == DataURI
        assert data_uri_from_file.mimetype == "text/plain"
        assert data_uri_from_file.is_base64
        assert type(data_uri_from_file.data) == bytes
        assert data_uri_from_file.data == content_file
        assert data_uri_from_file == "data:text/plain;base64,Y29udGVudCBvZiBhIGZpbGU="

    def test_from_data_uri_to_bytes_content_and_extension(
        self, dummy_content_and_data_uri
    ):
        content, dummy_data_uri = dummy_content_and_data_uri
        data_uri = DataURI(dummy_data_uri)

        content_file, extension = data_uri.to_content_bytes_and_extension()

        assert extension == ".pdf"
        assert type(content_file) == bytes
        assert content_file == content

    def test_make_data_uri_from_response_unknown(self, dummy_response_object):
        content_response = b"{'key_1': 'value', 'key_2': 'another'}"
        response = dummy_response_object("not valid content", content_response)

        with pytest.raises(ValueError):
            DataURI.from_response(response)

    def test_make_data_uri_from_response(self, dummy_response_object):
        content_response = b"{'key_1': 'value', 'key_2': 'another'}"
        response = dummy_response_object("application/json", content_response)

        data_uri_from_file = DataURI.from_response(response)

        assert type(data_uri_from_file) == DataURI
        assert data_uri_from_file.mimetype == "application/json"
        assert data_uri_from_file.is_base64
        assert type(data_uri_from_file.data) == bytes
        assert data_uri_from_file.data == content_response

    def test_make_data_uri_from_response_with_charset(self, dummy_response_object):
        content_response = b"{'key_1': 'value', 'key_2': 'another'}"
        response = dummy_response_object(
            "application/json;charset=utf-8", content_response
        )

        data_uri_from_file = DataURI.from_response(response)

        assert type(data_uri_from_file) == DataURI
        assert data_uri_from_file.mimetype == "application/json"
        assert data_uri_from_file.charset == "utf-8"
        assert data_uri_from_file.is_base64
        assert type(data_uri_from_file.data) == bytes
        assert data_uri_from_file.data == content_response
