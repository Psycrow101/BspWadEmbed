import io
import binary_reader
import bsp_texture


WAD_VERSION = 'WAD3'


class Wad(object):
    def __init__(self, file_path):
        with open(file_path, 'rb') as fd:
            if binary_reader.read_string(fd, strlen=4) != WAD_VERSION:
                raise Exception('WAD version must be "%s"!' % WAD_VERSION)

            textures_num, lump_offset = binary_reader.read_uint32(fd, num=2)
            self.textures = {}

            for i in range(textures_num):
                fd.seek(lump_offset + i * 32, io.SEEK_SET)
                texture_offset = binary_reader.read_uint32(fd)

                fd.seek(4, io.SEEK_CUR)
                texture_size = binary_reader.read_uint32(fd)

                fd.seek(4, io.SEEK_CUR)
                texture_name = binary_reader.read_string(fd, 16).lower()

                self.textures[texture_name] = bsp_texture.Texture.read(fd, texture_offset, texture_size)
