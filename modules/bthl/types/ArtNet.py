import struct

class ArtnetDMXPacket:
    _STRUCT = struct.Struct(
        "<8s H B B B B H B B 512s"
    )

    def __init__(self, universe=0, data=None, sequence=0, physical=0):
        self.id = b"Art-Net\x00"
        self.opCode = 0x5000          # ArtDMX (LE)
        self.protocolHi = 0x00
        self.protocolLo = 14
        self.sequence = sequence
        self.physical = physical
        self.universe = universe      # LE (Net/SubUni packed)
        self.length = 512             # BE
        self.data = data or bytes(512)

    def pack(self):
        length_hi = (self.length >> 8) & 0xFF
        length_lo = self.length & 0xFF

        return self._STRUCT.pack(
            self.id,
            self.opCode,
            self.protocolHi,
            self.protocolLo,
            self.sequence,
            self.physical,
            self.universe,
            length_hi,
            length_lo,
            self.data
        )
    
    @staticmethod
    def global_dict_to_packets(
        global_dmx: dict[int, int],
        sequence_start: int = 1,
        universe_offset: int = 0
    ):
        """
        Convert a global-channel DMX dict into ArtDMX packets.

        global_dmx[key] = value
        key = (universe - 1) * 512 + (channel - 1)
        """
        universes = {}
        packets = []

        # Group values by universe
        for global_channel, value in global_dmx.items():
            if value < 0 or value > 255:
                raise ValueError(f"Invalid DMX value {value}")

            universe = global_channel // 512          # 0-based
            channel  = global_channel % 512           # 0–511

            if universe not in universes:
                universes[universe] = bytearray(512)

            universes[universe][channel] = value

        # Build packets
        sequence = sequence_start
        for universe in sorted(universes.keys()):
            packet = ArtnetDMXPacket(
                universe=universe + universe_offset,
                data=bytes(universes[universe]),
                sequence=sequence
            )
            packets.append(packet)
            sequence = (sequence + 1) & 0xFF

        return packets

import struct
import socket

class ArtnetPollPacket:
    _STRUCT = struct.Struct(
        "<8s H 4s H H H B B H H B B B B 18s 64s 64s H B B 26s"
    )

    def __init__(
        self,
        ip: str,
        short_name: str,
        long_name: str,
        universe: int = 0,
        port: int = 0x1936  # 6454
    ):
        self.id = b"Art-Net\x00"
        self.opCode = 0x2100  # ArtPollReply (LE)

        self.ip = socket.inet_aton(ip)
        self.port = port

        self.verH = 0
        self.ver = 14

        self.netSwitch = 0
        self.subSwitch = 0

        self.oem = 0xFFFF
        self.ubea = 0
        self.status1 = 0b11000000  # indicators + normal operation

        self.estaMan = 0

        self.shortName = self._pad(short_name, 18)
        self.longName = self._pad(long_name, 64)
        self.nodeReport = self._pad("#0001 [OK]", 64)

        self.numPorts = 1
        self.portTypes = bytes([0x80, 0, 0, 0])   # DMX output
        self.goodOutput = bytes([0x80, 0, 0, 0])
        self.swOut = bytes([universe & 0xFF, 0, 0, 0])

        self.swVideo = 0
        self.swMacro = 0
        self.swRemote = 0

        self.style = 0x00  # Node
        self.mac = bytes(6)
        self.bindIp = self.ip
        self.bindIndex = 1
        self.status2 = 0

        self.filler = bytes(26)

    @staticmethod
    def _pad(text: str, length: int) -> bytes:
        b = text.encode("ascii", errors="ignore")[:length - 1]
        return b + b"\x00" + bytes(length - len(b) - 1)

    def pack(self):
        return self._STRUCT.pack(
            self.id,
            self.opCode,
            self.ip,
            self.port,
            self.verH,
            self.ver,
            self.netSwitch,
            self.subSwitch,
            self.oem,
            self.ubea,
            self.status1,
            self.estaMan,
            self.shortName,
            self.longName,
            self.nodeReport,
            self.numPorts,
            self.portTypes,
            self.goodOutput,
            self.swOut,
            self.swVideo,
            self.swMacro,
            self.swRemote,
            self.style,
            self.mac,
            self.bindIp,
            self.bindIndex,
            self.status2,
            self.filler
        )
