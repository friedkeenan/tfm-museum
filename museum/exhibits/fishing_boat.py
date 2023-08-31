import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Fishing_Boat(AdventureExhibit):
    adventure_id = 20

    map_code     = 2018
    map_xml_path = "Fishing/Boat.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    has_synchronizer = True

    incomplete = True
