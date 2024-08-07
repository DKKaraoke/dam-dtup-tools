"""DAM SPRC Header"""

from bitstring import BitStream, ReadError, pack
from fastcrc import crc16
from io import BufferedReader, BufferedWriter
from typing import Self


class DamSprcHeader:
    """DAM SPRC Header"""

    __MAGIC_BYTES = b"SPRC"

    @staticmethod
    def has_sprc_header(stream: BitStream | BufferedReader) -> bool:
        """Check SPRC header existance

        Args:
            stream (BitStream | BufferedReader): Source

        Returns:
            bool: True if source has SPRC header, else False
        """

        if isinstance(stream, BufferedReader):
            stream = BitStream(stream)

        try:
            sprc_header: bytes = stream.peek("bytes:16")
        except ReadError:
            return False
        magic_bytes = sprc_header[0:4]
        if magic_bytes != DamSprcHeader.__MAGIC_BYTES:
            return False
        return True

    @classmethod
    def read(cls, stream: BitStream | BufferedReader) -> Self:
        """Read from BitStream

        Args:
            stream (BitStream): Source

        Returns:
            Self: Xg8ReleaseVersionFile instance
        """

        if isinstance(stream, BufferedReader):
            stream = BitStream(stream)

        magic_bytes: bytes = stream.read("bytes:4")
        if magic_bytes != DamSprcHeader.__MAGIC_BYTES:
            raise ValueError(f"Invalid magic_bytes. magic_bytes={magic_bytes}")
        revision: int = stream.read("uintbe:16")
        crc_value: int = stream.read("uintbe:16")
        force_flag: int = stream.read("uint:8")
        unknown: bytes = stream.read("bytes:7")

        return cls(revision, crc_value, force_flag, unknown)

    def __init__(
        self, revision: int, crc_value: int, force_flag: int, unknown: bytes
    ) -> None:
        """Constructor

        Args:
            revision (int): Revision
            crc_value (int): CRC value
            force_flag (int): Force flag
            unknown (bytes): Unknown value
        """

        self.revision = revision
        self.crc_value = crc_value
        self.force_flag = force_flag
        self.unknown = unknown

    def validate_crc(self, data: bytes | BufferedReader) -> bool:
        """Validate data with CRC value

        Args:
            stream (BufferedReader): Message stream

        Returns:
            bool: True if data is valid, else False
        """

        if isinstance(data, BufferedReader):
            # Skip SPRC header
            data.seek(16)
            data = data.read()

        return crc16.genibus(data) == self.crc_value

    def write(self, stream: BitStream | BufferedWriter) -> None:
        """Write to BitStream

        Args:
            stream (BitStream): Destination
        """

        if isinstance(stream, BufferedWriter):
            stream = BitStream(stream)

        stream.append(b"SPRC")
        stream.append(pack("uintbe:16", self.revision))
        stream.append(pack("uintbe:16", self.crc_value))
        stream.append(pack("uint:8", self.force_flag))
        stream.append(self.unknown)
