import caseus

from ..exhibit import available
from ..shop    import Shops, ShopExhibit

@available
class Armageddon_Shop(ShopExhibit):
    map_code     = 2801
    map_xml_path = "Common/Shop.xml"

    map_category   = caseus.enums.MapCategory.UserMadeVanilla
    round_duration = 60

    original_year = 2024

    SEASHELL_VENDOR_X = 331
    SEASHELL_VENDOR_Y = 275

    # NOTE: These session IDs are taken from a real
    # example, however these session IDs change much
    # the same as the ones for the Greenhouse shop,
    # seeming to globally decrement per satellite server.
    STANDARD_VENDORS = {
        "Oracle": dict(
            session_id = -667,
            title_id   = 23,
            feminine   = True,
            look       = "61;0,0,0,0,0,19_3d100f+1fa896+ffe15b,0,0,0",
            x          = 595,
            y          = 275,
        ),

        "Indiana Mouse": dict(
            session_id = -668,
            title_id   = 27,
            feminine   = False,
            look       = "45;0,0,0,0,0,0,0,0,0",
            x          = 753,
            y          = 101,
        ),
    }

    NPC_SHOPS = {
        "Oracle": [
            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2480,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2257,
                cost_quantity = 50,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2616,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 20,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2251,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 5,
            ),
        ],

        "Indiana Mouse": Shops.INDIANA_MOUSE,
        "Luna":          Shops.LUNA_NINJA_2024,
        "Mousini":       Shops.MOUSINI,
        "Mauricette":    Shops.MAURICETTE,
        "Wu":            Shops.WU,
        "Rob":           Shops.ROB,
    }
