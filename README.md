# TFM Museum

A proxy for Transformice that allows a player to experience historic occasions such as events.

## Usage

To experience an exhibit of the museum, you must use [tfm-proxy-loader](https://github.com/friedkeenan/tfm-proxy-loader) to load Transformice, and also have [caseus](https://github.com/friedkeenan/caseus) installed. Then you can simply run the `museum.py` file according to the following usage:

```
usage: museum.py [-h] [--data-dir DATA_DIR] [--log] exhibit

positional arguments:
  exhibit              The exhibit to visit

options:
  -h, --help           show this help message and exit
  --data-dir DATA_DIR  The directory for the exhibit data (defaulted to 'data')
  --log                Log packets from the client and server
```

For instance, to run the "[Armageddon](https://transformice.fandom.com/wiki/Armageddon_2016)" exhibit you would do `./museum.py Armageddon`, and then use the proxy loader to load the game. The game will seem normal, but if you head to the map editor and click the "validate map" button, you will be loaded into the exhibit. There is no need to load any XMLs or otherwise mess with the map editor. To exit the exhibit, you may click the "map editor" button in the menu options or use the `/editor` command. This will bring you back to the map editor.

## Available Exhibits

The currently available exhibits are

- Armageddon

## Miscellaneous Tools

Contained within the '[tools](https://github.com/friedkeenan/tfm-museum/tree/main/tools)' directory are related but ancillary tools. These tools include:

- `make-archive.py`
    - This script will download `Transformice.swf`, `TransformiceChargeur.swf`, and the assets which are used by certain maps outside of the normal game assets, and will package them neatly in a folder along with the maps in question. This is important because as things are now, the museum will still cause the game to download certain assets from Transformice's servers, which is unideal for archival purposes. Keeping an archive however allows us to preserve the assets and create facilities to use the archived assets in case they ever become otherwise unavailable.
