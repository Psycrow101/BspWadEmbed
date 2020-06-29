import struct


def pack_int32(data, endian='<'):
    return struct.pack('%si' % endian, data)


def pack_uint32(data, endian='<'):
    return struct.pack('%sI' % endian, data)


def pack_string(string, strlen):
    return str.encode(string[:strlen] + '\x00' * (strlen - len(string)))
