"""XG8 DTUP File"""

from bitstring import BitStream
from io import BufferedReader, BufferedWriter
from typing import Self


class DamDtupSysexMessage:
    """DAM DTUP SysEx Message"""

    # YAMAHA
    __VENDOR_ID = 0x43
    __COMMAND_TYPE = 0x04
    __DEVICE_NUMBER = 0x01
    __MODEL_ID = 0x7F
    __UNKNOWN_0 = 0x03

    __MAX_PAYLOAD_SIZE = 0x800

    @staticmethod
    def calculate_checksum(message: bytes) -> int:
        """Calcurate Checksum

        Args:
            message (bytes): Message

        Returns:
            int: Checksum
        """

        return ~sum(message) + 1 & 0x7F

    @classmethod
    def read(cls, stream: BitStream | BufferedReader) -> Self | None:
        """Read from BitStream

        Args:
            stream (BitStream): Source

        Returns:
            Self: DamDtupSysexMessage instance
        """

        if isinstance(stream, BufferedReader):
            stream_bytepos = stream.tell()
            stream = BitStream(stream)
            stream.bytepos = stream_bytepos

        sysex_start: int = stream.read("uint:8")
        if sysex_start != 0xF0:
            return

        vendor_id: bytes = stream.read("uint:8")
        if vendor_id != DamDtupSysexMessage.__VENDOR_ID:
            raise ValueError(f"Invalid vendor_id. vendor_id={hex(vendor_id)}")
        command_type: int = stream.read("uint:4")
        if command_type != DamDtupSysexMessage.__COMMAND_TYPE:
            raise ValueError(f"Invalid command_type. command_type={hex(command_type)}")
        device_number: int = stream.read("uint:4")
        if device_number != DamDtupSysexMessage.__DEVICE_NUMBER:
            raise ValueError(
                f"Invalid device_number. device_number={hex(device_number)}"
            )
        model_id: bytes = stream.read("uint:8")
        if model_id != DamDtupSysexMessage.__MODEL_ID:
            raise ValueError(f"Invalid model_id. model_id={hex(model_id)}")
        unknown_0: bytes = stream.read("uint:8")
        if unknown_0 != DamDtupSysexMessage.__UNKNOWN_0:
            raise ValueError(f"Invalid unknown_0. unknown_0={hex(unknown_0)}")
        data_length_bytes: bytes = stream.read("bytes:2")
        data_length = data_length_bytes[0] << 7 | data_length_bytes[1]
        data: bytes = stream.read(f"bytes:{data_length}")

        data_checksum = DamDtupSysexMessage.calculate_checksum(data_length_bytes + data)
        checksum: int = stream.read("uint:8")
        if data_checksum != checksum:
            raise ValueError(
                f"Checksum mismatch. data_checksum={hex(data_checksum)} checksum={hex(checksum)}"
            )
        sysex_end: int = stream.read("uint:8")
        if sysex_end != 0xF7:
            raise ValueError(f"Invalid sysex_end. sysex_end={hex(sysex_end)}")

        return cls(bytes(data))

    def __init__(
        self,
        data: bytes,
    ) -> None:
        """Constructor

        Args:
            data (bytes): Data
        """

        self.data = data

    def write(self, stream: BitStream | BufferedWriter) -> None:
        """Write to BitStream

        Args:
            stream (BitStream): Destination
        """

        if isinstance(stream, BufferedWriter):
            stream_bytepos = stream.tell()
            stream = BitStream(stream)
            stream.bytepos = stream_bytepos

        # Stub


class DamDtupFile:
    """DAM DTUP File"""

    __MAGIC_BYTES = b"DTUP"

    @classmethod
    def read(cls, stream: BitStream | BufferedReader) -> Self:
        """Read from BitStream

        Args:
            stream (BitStream): Source

        Returns:
            Self: DamDtupFile instance
        """

        if isinstance(stream, BufferedReader):
            stream_bytepos = stream.tell()
            stream = BitStream(stream)
            stream.bytepos = stream_bytepos

        magic_bytes: bytes = stream.read("bytes:4")
        if magic_bytes != DamDtupFile.__MAGIC_BYTES:
            raise ValueError(f"Invalid magic_bytes. magic_bytes={magic_bytes}")
        size: int = stream.read("uintbe:32")
        target: int = stream.read("uintbe:32")
        version: bytes = stream.read("bytes:4")

        sysex_messages: list[DamDtupSysexMessage] = []
        data_start_position = stream.bytepos
        while True:
            if size <= stream.bytepos - data_start_position:
                break

            sysex_message = DamDtupSysexMessage.read(stream)
            if sysex_message is None:
                break
            sysex_messages.append(sysex_message)

        return cls(target, version, sysex_messages)

    def __init__(
        self,
        target: int,
        version: int,
        sysex_messages: list[DamDtupSysexMessage],
    ) -> None:
        """Constructor

        Args:
            target (int): Target
            version (int): Version
            sysex_messages (list[DamDtupSysexMessage]): SysEx messages
        """

        self.target = target
        self.version = version
        self.sysex_messages = sysex_messages

    def get_payload(self) -> bytes:
        """Get payload

        Returns:
            bytes: Payload
        """

        payload_stream = BitStream()
        for data_bits in [
            "0b" + "{0:07b}".format(data_byte)
            for sysex_message in self.sysex_messages
            for data_byte in sysex_message.data
        ]:
            payload_stream.append(data_bits)
        return payload_stream.tobytes()

    def write(self, stream: BitStream | BufferedWriter) -> None:
        """Write to BitStream

        Args:
            stream (BitStream): Destination
        """

        if isinstance(stream, BufferedWriter):
            stream_bytepos = stream.tell()
            stream = BitStream(stream)
            stream.bytepos = stream_bytepos

        # Stub
