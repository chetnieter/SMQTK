import base64
import hashlib
import re

from smqtk.exceptions import InvalidUriError
from smqtk.representation import DataElement

try:
    import magic
    # We know there are multiple modules named magic. Make sure the function we
    # expect is there.
    assert magic.detect_from_content is not None
except (ImportError, AttributeError, AssertionError):
    magic = None


class DataMemoryElement (DataElement):
    """
    In-memory representation of data stored in a byte list
    """

    # Base64 RE including URL-safe character replacements
    B64_PATTERN = '[a-zA-Z0-9+/_-]*={0,2}'
    DATA_B64_RE = re.compile('^base64://(?P<base64>{})$'.format(B64_PATTERN))
    DATA_URI_RE = re.compile("^data:(?P<ct>[\w/]+);base64,(?P<base64>{})$"
                             .format(B64_PATTERN))

    @classmethod
    def is_usable(cls):
        # No dependencies
        return True

    @classmethod
    def from_uri(cls, uri):
        """
        Construct a new instance based on the given URI.

        Memory elements resolve byte-string formats. Currently, this method
        accepts a base64 using the standard and URL-safe alphabet as the python
        ``base64.urlsafe_b64decode`` module function would expect.

        This method accepts URIs in two formats:
            - ``base64://<data>``
            - ``data:<mimetype>;base64,<data>``
            - Empty string (no data)

        Filling in ``<data>`` with the actual byte string, and ``<mimetype>``
        with the actual MIMETYPE of the bytes.

        This function uses the ``file-magic`` python module, which is an
        interface to libmagic, to detect content MIMETYPE. If this module is not
        present, we will set the content type to None.

        :param uri: URI string to resolve into an element instance
        :type uri: str

        :raises smqtk.exceptions.InvalidUriError: The given URI was not a base64
            format

        :return: New element instance of our type.
        :rtype: DataElement

        """
        if uri is None:
            raise InvalidUriError(uri, 'None value given')

        if len(uri) == 0:
            return DataMemoryElement('', None)

        data_b64_m = cls.DATA_B64_RE.match(uri)
        if data_b64_m is not None:
            m_d = data_b64_m.groupdict()
            return DataMemoryElement.from_base64(m_d['base64'], None)

        data_uri_m = cls.DATA_URI_RE.match(uri)
        if data_uri_m is not None:
            m_d = data_uri_m.groupdict()
            return DataMemoryElement.from_base64(
                m_d['base64'], m_d['ct']
            )

        raise InvalidUriError(uri, "Did not detect byte format URI")

    @classmethod
    def from_base64(cls, b64_str, content_type=None):
        """
        Create new MemoryElement instance based on a given base64 string and
        content type.

        This method accepts a base64 using the standard and URL-safe alphabet as
        the python ``base64.urlsafe_b64decode`` module function would expect.

        :param b64_str: Base64 data string.
        :type b64_str: str

        :param content_type: Content type string, or None if unknown.
        :type content_type: str | None

        :return: New MemoryElement instance containing the byte data in the
            given base64 string.
        :rtype: DataMemoryElement

        """
        if b64_str is None:
            raise ValueError("Base 64 string should not be None")
        return DataMemoryElement(base64.urlsafe_b64decode(b64_str), content_type)

    # noinspection PyShadowingBuiltins
    def __init__(self, bytes, content_type=None):
        """
        Create a new DataMemoryElement from a byte string and optional content
        type.

        :param bytes: Bytes to contains
        :type bytes: bytes | str

        :param content_type: Optional content type of the bytes given. If the
            ``file-magic`` module is installed and None is provided, a content
            type will be introspected from the byte content.
        :type content_type: None | str

        """
        super(DataMemoryElement, self).__init__()

        self._bytes = bytes
        self._content_type = content_type

    def get_config(self):
        return {
            "bytes": self._bytes,
            'content_type': self._content_type,
        }

    def content_type(self):
        """
        :return: Standard type/subtype string for this data element, or None if
            the content type is unknown.
        :rtype: str or None
        """
        # Lazy resolve content type if magic was importable
        if magic and self._content_type is None:
            self._content_type = magic.detect_from_content(self._bytes)\
                                      .mime_type
        return self._content_type

    def get_bytes(self):
        """
        :return: Get the byte stream for this data element.
        :rtype: bytes
        """
        return self._bytes


DATA_ELEMENT_CLASS = DataMemoryElement
