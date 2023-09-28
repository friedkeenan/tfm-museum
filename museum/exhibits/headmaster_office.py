import caseus

from ..exhibit import available
from ..shop    import Shops, ShopExhibit

@available
class Headmaster_Office(ShopExhibit):
    map_code     = 943
    map_author   = "_Headmaster's Office"
    map_xml_path = "School/HeadmasterOffice.xml"

    map_category   = caseus.enums.MapCategory.UserMadeVanilla
    round_duration = 60

    original_year = 2023

    SEASHELL_VENDOR_X = 338
    SEASHELL_VENDOR_Y = 267

    # NOTE: These session IDs are taken from a real
    # example, however these session IDs change much
    # the same as the ones for the Greenhouse shop,
    # seeming to globally decrement per satellite server.
    STANDARD_VENDORS = {
        "Prof": dict(
            session_id = -11219,
            title_id   = 327,
            feminine   = False,
            look       = "$Proviseur",
            x          = 752,
            y          = 200,

            # NOTE: The official server sets this
            # to 'False' while the other NPCs have
            # this as 'True'. This seems to be needed
            # for Prof to initially face the player,
            # who spawns on the far left of the map,
            # likely because of his look being a sprite.
            facing_right = False,
        ),

        "Indiana Mouse": dict(
            session_id = -11220,
            title_id   = 27,
            feminine   = False,
            look       = "45;0,0,0,0,0,0,0,0,0",
            x          = 412,
            y          = 242,
        ),

        "Mélo": dict(
            session_id = -11221,
            title_id   = 327,
            feminine   = False,
            look       = "1;108,36_d0202+95b6c9,0,0,0,0,0,25,0",
            x          = 520,
            y          = 222,
        ),
    }

    NPC_SHOPS = {
        "Prof": [
            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.ShopItem,
                item_id       = 484,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2335,
                cost_quantity = 80,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Cartouche,
                item_id       = 69,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2334,
                cost_quantity = 80,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Badge,
                item_id       = 432,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2334,
                cost_quantity = 50,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Badge,
                item_id       = 432,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2335,
                cost_quantity = 50,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Title,
                item_id       = 562,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2334,
                cost_quantity = 150,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Title,
                item_id       = 564,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2335,
                cost_quantity = 40,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2483,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2257,
                cost_quantity = 50,
            ),
        ],

        "Indiana Mouse": Shops.INDIANA_MOUSE,

        "Mélo": [
            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Emoji,
                item_id       = 20003,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2586,
                cost_quantity = 20,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2257,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2334,
                cost_quantity = 4,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2257,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2335,
                cost_quantity = 10,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2584,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 10,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2585,
                quantity      = 5,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 5,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 25,
                quantity      = 15,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2335,
                cost_quantity = 1,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 26,
                quantity      = 15,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2335,
                cost_quantity = 1,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 4,
                quantity      = 10,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2335,
                cost_quantity = 1,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2497,
                quantity      = 10,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2335,
                cost_quantity = 1,
            ),
        ],

        "Luna":       Shops.LUNA_BACK_TO_SCHOOL_2023,
        "Mousini":    Shops.MOUSINI,
        "Mauricette": Shops.MAURICETTE,
        "Wu":         Shops.WU,
        "Rob":        Shops.ROB,
    }
