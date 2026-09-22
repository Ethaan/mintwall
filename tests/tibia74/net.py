"""Little-endian message reader/writer for the Tibia 7.4 wire format."""
import struct


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def remaining(self) -> int:
        return len(self.data) - self.pos

    def u8(self) -> int:
        v = self.data[self.pos]
        self.pos += 1
        return v

    def peek_u8(self) -> int:
        return self.data[self.pos]

    def u16(self) -> int:
        v = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def peek_u16(self) -> int:
        return struct.unpack_from("<H", self.data, self.pos)[0]

    def u32(self) -> int:
        v = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return v

    def string(self) -> str:
        n = self.u16()
        s = self.data[self.pos:self.pos + n].decode("latin-1")
        self.pos += n
        return s

    def position(self) -> tuple:
        return (self.u16(), self.u16(), self.u8())

    def skip(self, n: int):
        self.pos += n


class Writer:
    def __init__(self):
        self.buf = bytearray()

    def u8(self, v):
        self.buf += struct.pack("<B", v)
        return self

    def u16(self, v):
        self.buf += struct.pack("<H", v)
        return self

    def u32(self, v):
        self.buf += struct.pack("<I", v)
        return self

    def string(self, s: str):
        b = s.encode("latin-1")
        self.u16(len(b))
        self.buf += b
        return self

    def position(self, pos):
        x, y, z = pos
        return self.u16(x).u16(y).u8(z)

    def packet(self) -> bytes:
        """Frame with the 2-byte length header (7.4 has no checksum or encryption)."""
        return struct.pack("<H", len(self.buf)) + bytes(self.buf)
