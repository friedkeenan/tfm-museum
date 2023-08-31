import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Fishing_Shipwreck(AdventureExhibit):
    adventure_id = 20

    map_code     = 919
    map_author   = "_peche"
    map_xml_path = "Fishing/Shipwreck.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    has_synchronizer = True

    incomplete = True

    # TODO: NPC.
    # DisableInitialItemCooldownPacket after adding NPC.

    # Trampolines get spawned 50 units in front of player, velocity x and y are 1, uses addshamanobject to everyone, velocity x negative if facing left. Cooldown 60.
    # Ghost box same except gets spawned 30 in front of player, 20 below. Cooldown unknown, I think 60?
