import io
import re
import os
from collections import OrderedDict

import binary_reader
import binary_writer
import data_unpacker
import bsp_texture


HL_VERSION = 30
LUMPS_NUM = 15

LUMPS_ORDER = (1, 10, 3, 5, 6, 7, 9, 11, 13, 12, 14, 8, 4, 0, 2)


class Lump(object):
    def __init__(self, rawdata):
        self.__rawdata = rawdata

    def __len__(self):
        return len(self.__rawdata)

    @classmethod
    def read(cls, fd, offset, size):
        fd.seek(offset, io.SEEK_SET)
        return cls(fd.read(size))

    def write(self, fd):
        fd.write(self.__rawdata)


class EntitiesLump(Lump):
    def __init__(self, rawdata):
        Lump.__init__(self, rawdata)

        self.entities = []
        for s in re.findall(r'{[^}]+}', re.sub('\r', '', rawdata.decode('cp437')), re.DOTALL):
            values = OrderedDict()
            for p in re.sub('{\n|\n}', '', s).split('\n'):
                val = re.findall(r'"[^"]*"', p)
                if not val:
                    continue
                values[re.sub('"', '', val[0])] = re.sub('"', '', val[1])
            self.entities.append(values)

    def __len__(self):
        size = 1
        for ent in self.entities:
            for key, val in ent.items():
                size += len(key) + len(val) + 6
            size += 4

        return size

    def write(self, fd, put_zero_end: bool = True):
        for ent in self.entities:
            fd.write(b'{\n')
            for key, val in ent.items():
                fd.write(str.encode(f'"{key}" "{val}"\n'))
            fd.write(b'}\n')
        if put_zero_end:
            fd.write(b'\0')


class TexturesLump(Lump):
    def __init__(self, rawdata):
        Lump.__init__(self, rawdata)

        textures_num = data_unpacker.unpack_uint32(rawdata[:4])
        cur_pos = 4

        offsets = data_unpacker.unpack_uint32(rawdata[cur_pos:cur_pos + 4 * textures_num], num=textures_num)
        cur_pos += 4 * textures_num

        # todo: test
        offsets = [o for o in offsets if o != 0xffffffff]

        self.textures = [bsp_texture.Texture(rawdata[o:]) for o in offsets]

    def __len__(self):
        return 4 + 4 * len(self.textures) + sum(map(len, self.textures))

    def write(self, fd):
        textures_num = len(self.textures)

        binary_writer.write_uint32(fd, textures_num)

        cur_offset = 4 + textures_num * 4
        for texture in self.textures:
            binary_writer.write_uint32(fd, cur_offset)
            cur_offset += len(texture)

        cur_offset = 4 + textures_num * 4
        for texture in self.textures:
            fd.write(texture.pack(cur_offset))
            cur_offset += len(texture)


LUMPS_CLASSES = (
    EntitiesLump,
    Lump,
    TexturesLump,
    Lump,
    Lump,
    Lump,
    Lump,
    Lump,
    Lump,
    Lump,
    Lump,
    Lump,
    Lump,
    Lump,
    Lump
)


class Bsp(object):
    def __init__(self, file_path):
        with open(file_path, 'rb') as fd:
            if binary_reader.read_uint32(fd) != HL_VERSION:
                raise Exception('BSP version must be %d!' % HL_VERSION)

            # self.name = os.path.basename(file_path)

            lumps_location = [(binary_reader.read_int32(fd), binary_reader.read_int32(fd)) for _ in range(LUMPS_NUM)]
            self.__lumps = [LUMPS_CLASSES[i].read(fd, offset, size)
                            for i, (offset, size) in enumerate(lumps_location)]
            self.__lumps_ordered = [self.__lumps[LUMPS_ORDER[i]] for i in range(LUMPS_NUM)]

    def __len__(self):
        return sum(len(lump) for lump in self.__lumps)

    @property
    def entities_lump(self) -> EntitiesLump:
        return self.__lumps[0]

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as fd:
            binary_writer.write_uint32(fd, HL_VERSION)

            cur_offset = LUMPS_NUM * 8 + 4
            lump_offsets = {}

            for lump in self.__lumps_ordered:
                lump_offsets[lump] = cur_offset
                cur_offset += len(lump)

            for lump in self.__lumps:
                binary_writer.write_int32(fd, lump_offsets[lump])
                binary_writer.write_int32(fd, len(lump))

            for lump in self.__lumps_ordered:
                lump.write(fd)

    def get_wad_names(self):
        for ent in self.__lumps[0].entities:
            if 'classname' in ent.keys() and 'wad' in ent.keys() and ent['classname'] == 'worldspawn':
                return [os.path.basename(w).lower() for w in ent['wad'].split(';') if w]
        return []

    def get_textures(self):
        return self.__lumps[2].textures

    # todo: move to EntityLump
    def remove_entities_key(self, finder_key, finder_value, key):
        for ent in self.__lumps[0].entities:
            if finder_key not in ent.keys() or key not in ent.keys():
                continue

            if ent[finder_key] == finder_value:
                del ent[key]
