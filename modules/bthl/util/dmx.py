import math
from bthl.util.general import scale_number
import struct
from mathutils import Vector, Quaternion, Euler

def getPositionAsDMX(loc: Vector, range: int, bytesPerAxis: int = 1) -> bytearray:
    #clamp the location to the specified range to avoid overflow
    old_loc = loc.copy()
    loc.x = max(min(loc.x, range), -range)
    loc.y = max(min(loc.y, range), -range)
    loc.z = max(min(loc.z, range), -range)

    #check if we had to clamp
    if loc != old_loc:
        print(f"Warning: Location {old_loc} was out of range and has been clamped to {loc}")

    xscale = int(scale_number(loc.x, 0, (2**(8*bytesPerAxis))-1, -range, range))
    yscale = int(scale_number(loc.y, 0, (2**(8*bytesPerAxis))-1, -range, range))
    zscale = int(scale_number(loc.z, 0, (2**(8*bytesPerAxis))-1, -range, range))
    #print("Position Values:", loc.x, loc.y, loc.z)
    #print("DMX Position Scaled:", xscale, yscale, zscale)
    #now convert to bytes
    xbytes = struct.pack('>I', xscale)[-bytesPerAxis:]
    ybytes = struct.pack('>I', yscale)[-bytesPerAxis:]
    zbytes = struct.pack('>I', zscale)[-bytesPerAxis:]
    return bytearray(xbytes + ybytes + zbytes)

def getPanTiltAsDMX(pan: float, tilt: float, panRange: int, tiltRange: int, bytesPerAxis: int = 2) -> bytearray:
    pan_remapped = int(scale_number(pan, 0, (2**(8*bytesPerAxis))-1, 0, panRange))
    tilt_remapped = int(scale_number(tilt, 0, (2**(8*bytesPerAxis))-1, 0, tiltRange))
    #now convert to bytes
    panbytes = struct.pack('>I', pan_remapped)[-bytesPerAxis:]
    tiltbytes = struct.pack('>I', tilt_remapped)[-bytesPerAxis:]
    return bytearray(panbytes + tiltbytes)

def getRotationAsDMX(rot: Euler, range: int, bytesPerAxis: int = 1) -> bytearray:
    #constrict to 360 degrees as theres no point going beyond
    rot.x = rot.x % math.radians(360)
    rot.y = rot.y % math.radians(360)
    rot.z = rot.z % math.radians(360)
    #0 is the valid start for this range in this case
    xscale = int(scale_number(rot.x, 0, (2**(8*bytesPerAxis))-1, 0, range))
    yscale = int(scale_number(rot.y, 0, (2**(8*bytesPerAxis))-1, 0, range))
    zscale = int(scale_number(rot.z, 0, (2**(8*bytesPerAxis))-1, 0, range))
    #now convert to bytes
    xbytes = struct.pack('>I', xscale)[-bytesPerAxis:]
    ybytes = struct.pack('>I', yscale)[-bytesPerAxis:]
    zbytes = struct.pack('>I', zscale)[-bytesPerAxis:]
    return bytearray(xbytes + ybytes + zbytes)

def getQuaternionAsDMX(rot: Quaternion, range: int, bytesPerAxis: int = 1) -> bytearray:
    xscale = int(scale_number(rot.x, 0, (2**(8*bytesPerAxis))-1, -range, range))
    yscale = int(scale_number(rot.y, 0, (2**(8*bytesPerAxis))-1, -range, range))
    zscale = int(scale_number(rot.z, 0, (2**(8*bytesPerAxis))-1, -range, range))
    wscale = int(scale_number(rot.w, 0, (2**(8*bytesPerAxis))-1, -range, range))
    #now convert to bytes
    xbytes = struct.pack('>I', xscale)[-bytesPerAxis:]
    ybytes = struct.pack('>I', yscale)[-bytesPerAxis:]
    zbytes = struct.pack('>I', zscale)[-bytesPerAxis:]
    wbytes = struct.pack('>I', wscale)[-bytesPerAxis:]
    return bytearray(xbytes + ybytes + zbytes + wbytes)

def getColorAsDMX(color: tuple[float, float, float]) -> bytes:
    return getTupleAsDMX(color)

def getTupleAsDMX(tup: tuple) -> bytes:
    barray = bytearray()
    for val in tup:
        if isinstance(val, float):
            scaled = int(scale_number(val, 0,255,0,1))
            barray.append(scaled)
        elif isinstance(val, int):
            barray.append(val)
    return bytes(barray)
