import errno
import sys
import os
import argparse
import bsp
import wad


ADDITIONAL_WADS_FILE = 'additional_wad.ini'


def get_additional_wads():
    additional_wads_file = os.path.join(os.path.dirname(__file__), ADDITIONAL_WADS_FILE)

    if os.path.exists(additional_wads_file):
        with open(additional_wads_file, 'r') as fd:
            return [l.strip() for l in fd.readlines() if l.strip()]
    return None


def inject_wad(input_file, output_file, wad_directory, force_wad):
    bsp_file = bsp.Bsp(input_file)
    wad_names = bsp_file.get_wad_names()

    if not wad_names and not force_wad:
        print('This BSP file contains no external wad files')
        sys.exit(0)

    bsp_textures = bsp_file.get_textures()
    wad_files = [wad.Wad(os.path.join(wad_directory, wad_path))
                 for wad_path in os.listdir(wad_directory) if wad_path.lower() in wad_names]

    if force_wad and force_wad not in wad_files:
        wad_files.append(wad.Wad(force_wad))

    additional_wads = get_additional_wads()
    if additional_wads:
        wad_files += [wad.Wad(w) for w in additional_wads if w not in wad_files]

    for i, texture in enumerate(bsp_textures):
        texture_name, donor_texture = texture.get_name(), None

        if texture.is_embedded() and not force_wad:
            continue

        for w in wad_files:
            if texture_name in w.textures.keys():
                donor_texture = w.textures[texture_name]
                break

        if not donor_texture and not texture.is_embedded():
            raise Exception('Texture "%s" not found in WAD files' % texture_name)

        if donor_texture:
            bsp_textures[i] = donor_texture

    bsp_file.remove_entities_key('classname', 'worldspawn', 'wad')
    bsp_file.write_to_file(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True, help='input BSP file')
    parser.add_argument('--output', '-o', help='output BSP file')
    parser.add_argument('--wad_dir', '-w', help='directory with WAD files')
    parser.add_argument('--force_wad', '-f', help='force embed textures from the specified WAD file')

    args = parser.parse_args()

    output = args.output if args.output else args.input[:-4] + '_nowad.bsp'
    wad_dir = args.wad_dir if args.wad_dir else os.path.dirname(args.input)

    try:
        inject_wad(args.input, output, wad_dir, args.force_wad)
    except IOError as e:
        print(e)
        sys.exit(errno.ENOENT)
    except Exception as e:
        print(e)
        sys.exit(1)

    print('Done!')
