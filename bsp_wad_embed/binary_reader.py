import struct


def read_int32(fd, num=1, endian='<'):
    data = struct.unpack('%s%di' % (endian, num), fd.read(4 * num))
    return data if num > 1 else data[0]


def read_uint32(fd, num=1, endian='<'):
    data = struct.unpack('%s%dI' % (endian, num), fd.read(4 * num))
    return data if num > 1 else data[0]


def read_float(fd, num=1, endian='<'):
    data = struct.unpack('%s%df' % (endian, num), fd.read(4 * num))
    return data if num > 1 else data[0]


def read_string(fd, strlen=0):
    str_start, string, cur_index = fd.tell(), '', 0
    byte = fd.read(1)
    while byte != b'\x00':
        if strlen and cur_index == strlen:
            break
        string += byte.decode('cp437')
        byte = fd.read(1)
        cur_index += 1
    if strlen > 0:
        fd.seek(strlen - fd.tell() + str_start, 1)
        return string[:strlen]
    return string
