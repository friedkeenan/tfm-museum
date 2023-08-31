import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Fishing_Beach(AdventureExhibit):
    adventure_id = 20

    map_code     = 923
    map_author   = "_peche"
    map_xml_path = "Fishing/Beach.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    incomplete = True

    # TODO: NPC.
