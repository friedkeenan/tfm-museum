import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

# TODO: Common base class for relic/fishing maps?

@available
class Fishing_Jungle(AdventureExhibit):
    adventure_id = 20

    map_code     = 920
    map_author   = "_peche"
    map_xml_path = "Fishing/Jungle.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    incomplete = True

    # Relic is acquired every 10-15 seconds after casting rod.
