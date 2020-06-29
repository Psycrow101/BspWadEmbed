import io
import data_unpacker
import data_packer


class Texture(object):
    def __init__(self, rawdata):
        self.__name = data_unpacker.unpack_string(rawdata[:16]).lower()

        cur_pos = 16

        self.__width, self.__height = data_unpacker.unpack_uint32(rawdata[cur_pos:cur_pos + 8], num=2)
        offset = data_unpacker.unpack_uint32(rawdata[cur_pos + 8:cur_pos + 12])
        cur_pos += 24

        other_data_len = 0
        if offset:
            other_data_len += self.__width * self.__height + 772
            other_data_len += (self.__width / 2) * (self.__height / 2)
            other_data_len += (self.__width / 4) * (self.__height / 4)
            other_data_len += (self.__width / 8) * (self.__height / 8)

        other_data_len = int(other_data_len)

        self.__image_data = rawdata[cur_pos: cur_pos + other_data_len]
        self.__full_size = cur_pos + other_data_len

    def __len__(self):
        return self.__full_size

    @classmethod
    def read(cls, fd, offset, size):
        fd.seek(offset, io.SEEK_SET)
        return cls(fd.read(size))

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name[:16]

    def is_embedded(self):
        return len(self.__image_data) > 0

    def pack(self, pos):
        res = data_packer.pack_string(self.__name, 16)
        res += data_packer.pack_uint32(self.__width)
        res += data_packer.pack_uint32(self.__height)

        if len(self.__image_data):
            img_pos = pos + 40
            res += data_packer.pack_uint32(img_pos)

            img_pos += self.__width * self.__height
            res += data_packer.pack_uint32(img_pos)

            img_pos += int((self.__width / 2) * (self.__height / 2))
            res += data_packer.pack_uint32(img_pos)

            img_pos += int((self.__width / 4) * (self.__height / 4))
            res += data_packer.pack_uint32(img_pos)
        else:
            for _ in range(4):
                res += data_packer.pack_uint32(0)

        res += self.__image_data

        return res
