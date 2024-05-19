import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Flappy_Mouse(AdventureExhibit):
    adventure_id = 23

    map_code     = 948
    map_author   = "_Halloween 2015"
    map_xml_path = "Halloween/FlappyMouse.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    round_duration = 60

    incomplete = True

    # TODO: Actually generating the grounds.
