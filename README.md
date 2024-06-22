# TFM Museum

A utility for Transformice that allows a player to experience historic occasions such as events.

## Usage

To experience an exhibit of the museum, you must use [tfm-proxy-loader](https://github.com/friedkeenan/tfm-proxy-loader) to load Transformice, and also have [caseus](https://github.com/friedkeenan/caseus) installed. Then you can simply run the `python -m museum` command according to the following usage:

```
usage: museum [-h] [--data-dir DATA_DIR] [--log]

options:
  -h, --help           show this help message and exit
  --data-dir DATA_DIR  The directory for the exhibit data (defaulted to 'data')
  --log                Log packets from the client and server
```

This will run a server implementation running on `localhost:11801` that you can connect to using the proxy loader. To enter the museum, simply get to the login page, enter a username, and press the "Submit" button; passwords are ignored. If your username is not already taken, then you will be welcomed into the museum. The rooms you enter correspond to the exhibits you can visit. For instance, going to the "armageddon" room will bring you to the "[Armageddon](https://transformice.fandom.com/wiki/Armageddon_2016)" exhibit. If you go to a room with no corresponding exhibit, you will be brought to the lobby, which is not a very exciting place.

Please note that this server is **NOT** intended for a general audience. It implicitly trusts clients, and does not attempt much of any error handling, nor does it care that much about performance. Using this server for a general audience is a decidedly bad idea. Do not do it.

## Showcase

https://user-images.githubusercontent.com/20881398/230795738-b1790f6f-ed2e-4158-bd5c-826eb613010e.mp4

## Available Exhibits

The currently available exhibits are:

- [Armageddon](https://transformice.fandom.com/wiki/Armageddon_2016)
- [Armageddon_Shop](https://transformice.fandom.com/wiki/Armageddon_2024#Shops)
- [Astrological](https://transformice.fandom.com/wiki/Astrological_2016)
- [Dance](https://transformice.fandom.com/wiki/Back_to_School_2023#Dance)
- [Dino](https://transformice.fandom.com/wiki/Dino_2016)
- [Dragon](https://transformice.fandom.com/wiki/Dragon_2016)
- **INCOMPLETE** [Epiphany](https://transformice.fandom.com/wiki/Epiphany_2016)
- **INCOMPLETE** [Fishing_Beach](https://transformice.fandom.com/wiki/Fishing_2023)
- **INCOMPLETE** [Fishing_Boat](https://transformice.fandom.com/wiki/Fishing_2023)
- **INCOMPLETE** [Fishing_Jungle](https://transformice.fandom.com/wiki/Fishing_2023)
- **INCOMPLETE** [Fishing_Shipwreck](https://transformice.fandom.com/wiki/Fishing_2023)
- **INCOMPLETE** [Flappy_Mouse](https://transformice.fandom.com/wiki/Halloween_2023#Broom)
- [Geography](https://transformice.fandom.com/wiki/Back_to_School_2023#Geography)
- [Greenhouse](https://transformice.fandom.com/wiki/Greenhouse_2021)
- [Greenhouse_Shop](https://transformice.fandom.com/wiki/Greenhouse_2023#Shops)
- [Headmaster_Office](https://transformice.fandom.com/wiki/Back_to_School_2023#Headmaster's_office)
- [Ninja](https://transformice.fandom.com/wiki/Ninja_2024)
- [Rain](https://transformice.fandom.com/wiki/Rain_2016)
- [Running_Track](https://transformice.fandom.com/wiki/Back_to_School_2023#Running_track)
- **INCOMPLETE** [Wizard](https://transformice.fandom.com/wiki/Wizard_2017)

## Miscellaneous Tools

Contained within the '[tools](https://github.com/friedkeenan/tfm-museum/tree/main/tools)' directory are related but ancillary tools. These tools include:

- `make-archive.py`
    - This script will download `Transformice.swf`, `TransformiceChargeur.swf`, and the assets which are used by certain maps outside of the normal game assets, and will package them neatly in a folder along with the maps in question. This is important because as things are now, the museum will still cause the game to download certain assets from Transformice's servers, which is unideal for archival purposes. Keeping an archive however allows us to preserve the assets and create facilities to use the archived assets in case they ever become otherwise unavailable.
