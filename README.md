# BspWadEmbed

My old script for embedding a WAD texture archive in a BSP map (GoldSrc). One of the features of this script is the quick replacement of textures on the map.

## Usage

The script is written in Python 3.

```
python bsp_wad_embed.py [-h] --input INPUT [--output OUTPUT]
                        [--wad_dir WAD_DIR] [--force_wad FORCE_WAD]

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        input BSP file
  --output OUTPUT, -o OUTPUT
                        output BSP file
  --wad_dir WAD_DIR, -w WAD_DIR
                        directory with WAD files
  --force_wad FORCE_WAD, -f FORCE_WAD
                        force embed textures from the specified WAD file
```

_The additional_wad.ini configuration file contains the paths to additional textures that the BSP map uses._

## Usage example

A few usage examples:

```sh
python -i "C:/Half-Life/map.bsp" -o "C:/Half-Life/map_nowad.bsp" -w "C:/Half-Life/cstrike"
```

```sh
python -i "C:/Half-Life/map.bsp" -o "C:/Half-Life/map_with_new_textures.bsp" -f "C:/Half-Life/replacement.wad"
```
