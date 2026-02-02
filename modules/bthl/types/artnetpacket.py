import struct

class ArtnetPacket:
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
        sequence_start: int = 1
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
            packet = ArtnetPacket(
                universe=universe,
                data=bytes(universes[universe]),
                sequence=sequence
            )
            packets.append(packet)
            sequence = (sequence + 1) & 0xFF

        return packets

