import struct


def write_int32(fd, val, endian='<'):
    fd.write(struct.pack('%si' % endian, val))


def write_uint32(fd, val, endian='<'):
    fd.write(struct.pack('%sI' % endian, val))
