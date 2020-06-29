import struct


def unpack_int32(data, num=1, endian='<'):
    res = struct.unpack('%s%di' % (endian, num), data)
    return res if num > 1 else res[0]


def unpack_uint32(data, num=1, endian='<'):
    res = struct.unpack('%s%dI' % (endian, num), data)
    return res if num > 1 else res[0]


def unpack_string(data):
    string = ''
    for c in data:
        # if c == b'\x00':
        if c == 0:
            break
        # string += c.decode('ascii').encode('ascii')
        string += chr(c)
    return string
